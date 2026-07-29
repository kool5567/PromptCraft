from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from celery import Task
from sqlalchemy.ext.asyncio import AsyncSession, async_session_factory
from sqlalchemy import select

from app.core.database import async_session_factory
from app.models.import_log import ImportLog
from app.models.prompt import Prompt, PromptStatus
from app.models.user import User
from app.tasks.celery_app import celery_app
from app.utils.github_client import GitHubClient

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    _session: Optional[AsyncSession] = None

    @property
    def session(self) -> AsyncSession:
        return self._session

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if self._session is not None:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._session.close())
                else:
                    loop.run_until_complete(self._session.close())
            except Exception:
                pass
            self._session = None


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, name="process_github_import")
def process_github_import(
    self: DatabaseTask,
    import_log_id: int,
    repo_url: str,
    user_id: int,
) -> dict[str, Any]:
    import asyncio

    async def _run() -> dict[str, Any]:
        async with async_session_factory() as session:
            try:
                log_result = await session.execute(
                    select(ImportLog).where(ImportLog.id == import_log_id)
                )
                import_log = log_result.scalar_one_or_none()
                if not import_log:
                    raise ValueError(f"ImportLog {import_log_id} not found")

                import_log.status = "processing"
                import_log.started_at = datetime.now(timezone.utc)
                await session.commit()

                client = GitHubClient()
                prompts = await client.import_from_repo(repo_url)
                total = len(prompts)
                imported = 0
                failed = 0

                for prompt_data in prompts:
                    try:
                        title = prompt_data.get("title", "Untitled Prompt")
                        content = prompt_data.get("content", "")
                        if not content:
                            failed += 1
                            continue

                        user_result = await session.execute(
                            select(User).where(User.id == user_id)
                        )
                        user = user_result.scalar_one_or_none()
                        if not user:
                            failed += 1
                            continue

                        prompt = Prompt(
                            user_id=user_id,
                            title=title[:255],
                            content=content,
                            description=prompt_data.get("description", "")[:500] if prompt_data.get("description") else None,
                            is_public=False,
                            is_premium=False,
                            is_template=False,
                            status=PromptStatus.DRAFT,
                            imported_from=repo_url,
                        )
                        session.add(prompt)
                        await session.flush()
                        imported += 1
                    except Exception as e:
                        failed += 1
                        logger.error(f"Failed to import prompt: {e}")
                        continue

                import_log.total_items = total
                import_log.imported_items = imported
                import_log.failed_items = failed
                import_log.status = "completed"
                import_log.completed_at = datetime.now(timezone.utc)
                await session.commit()

                return {
                    "import_log_id": import_log_id,
                    "status": "completed",
                    "total": total,
                    "imported": imported,
                    "failed": failed,
                }

            except Exception as exc:
                try:
                    log_result = await session.execute(
                        select(ImportLog).where(ImportLog.id == import_log_id)
                    )
                    import_log = log_result.scalar_one_or_none()
                    if import_log:
                        import_log.status = "failed"
                        import_log.error_message = str(exc)
                        import_log.completed_at = datetime.now(timezone.utc)
                        await session.commit()
                except Exception:
                    pass

                logger.error(f"GitHub import failed: {exc}")
                raise self.retry(exc=exc)

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30, name="process_file_import")
def process_file_import(
    self: DatabaseTask,
    import_log_id: int,
    file_content: str,
    user_id: int,
    source: str = "file_upload",
) -> dict[str, Any]:
    import asyncio
    import json
    import yaml  # optional

    async def _run() -> dict[str, Any]:
        async with async_session_factory() as session:
            try:
                log_result = await session.execute(
                    select(ImportLog).where(ImportLog.id == import_log_id)
                )
                import_log = log_result.scalar_one_or_none()
                if not import_log:
                    raise ValueError(f"ImportLog {import_log_id} not found")

                import_log.status = "processing"
                import_log.started_at = datetime.now(timezone.utc)
                await session.commit()

                prompts_data: list[dict[str, Any]] = []
                try:
                    parsed = json.loads(file_content)
                    if isinstance(parsed, list):
                        prompts_data = parsed
                    elif isinstance(parsed, dict):
                        if "prompts" in parsed:
                            prompts_data = parsed["prompts"]
                        else:
                            prompts_data = [parsed]
                except json.JSONDecodeError:
                    try:
                        parsed = yaml.safe_load(file_content)
                        if isinstance(parsed, list):
                            prompts_data = parsed
                        elif isinstance(parsed, dict):
                            if "prompts" in parsed:
                                prompts_data = parsed["prompts"]
                            else:
                                prompts_data = [parsed]
                    except Exception:
                        prompts_data = [{"title": "Imported Prompt", "content": file_content}]

                total = len(prompts_data)
                imported = 0
                failed = 0

                for item in prompts_data:
                    try:
                        title = item.get("title") or item.get("name", "Untitled Prompt")
                        content = item.get("content") or item.get("prompt", "")
                        if not content:
                            failed += 1
                            continue

                        prompt = Prompt(
                            user_id=user_id,
                            title=str(title)[:255],
                            content=str(content),
                            description=str(item.get("description", ""))[:500] if item.get("description") else None,
                            is_public=False,
                            is_premium=False,
                            is_template=False,
                            status=PromptStatus.DRAFT,
                            imported_from=source,
                        )
                        session.add(prompt)
                        await session.flush()
                        imported += 1
                    except Exception as e:
                        failed += 1
                        logger.error(f"Failed to import from file: {e}")
                        continue

                import_log.total_items = total
                import_log.imported_items = imported
                import_log.failed_items = failed
                import_log.status = "completed"
                import_log.completed_at = datetime.now(timezone.utc)
                await session.commit()

                return {
                    "import_log_id": import_log_id,
                    "status": "completed",
                    "total": total,
                    "imported": imported,
                    "failed": failed,
                }

            except Exception as exc:
                try:
                    log_result = await session.execute(
                        select(ImportLog).where(ImportLog.id == import_log_id)
                    )
                    import_log = log_result.scalar_one_or_none()
                    if import_log:
                        import_log.status = "failed"
                        import_log.error_message = str(exc)
                        import_log.completed_at = datetime.now(timezone.utc)
                        await session.commit()
                except Exception:
                    pass

                logger.error(f"File import failed: {exc}")
                raise self.retry(exc=exc)

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_run())
    finally:
        loop.close()
