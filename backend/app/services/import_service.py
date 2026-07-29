from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.repositories import ImportLogRepository, PromptRepository, TagRepository
from app.schemas.import_log import ImportListResponse, ImportResponse


class ImportService:
    def __init__(self, db: AsyncSession) -> None:
        self.import_repo = ImportLogRepository(db)
        self.prompt_repo = PromptRepository(db)
        self.tag_repo = TagRepository(db)

    async def import_from_github(self, user_id: int, repo_url: str) -> dict:
        repo_url = repo_url.rstrip("/")
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]

        match = re.match(r"https?://github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            raise BadRequestException("Invalid GitHub repository URL")

        owner, repo = match.group(1), match.group(2)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

        headers = {"Accept": "application/vnd.github.v3+json"}
        if settings.github_access_token:
            headers["Authorization"] = f"Bearer {settings.github_access_token}"

        log = await self.import_repo.create(
            imported_by=user_id,
            source="github",
            source_url=repo_url,
            total_items=0,
            imported_items=0,
            failed_items=0,
            status="processing",
            started_at=datetime.now(timezone.utc),
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(api_url, headers=headers)
                resp.raise_for_status()
                items = resp.json()

            prompt_files = [item for item in items if item["name"].endswith((".md", ".txt", ".json"))]
            imported = 0
            failed = 0

            for file_item in prompt_files:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        file_resp = await client.get(file_item["download_url"], headers=headers)
                        file_resp.raise_for_status()
                        content = file_resp.text

                    title = file_item["name"].rsplit(".", 1)[0]
                    description = f"Imported from GitHub: {repo_url}"

                    await self.prompt_repo.create(
                        user_id=user_id,
                        title=title,
                        content=content,
                        description=description,
                        imported_from=repo_url,
                        is_public=False,
                    )
                    imported += 1
                except Exception:
                    failed += 1

            total = len(prompt_files)
            await self.import_repo.update_status(
                id=log.id,
                status="completed",
            )
            log_obj = await self.import_repo.get(log.id)
            if log_obj:
                log_obj.total_items = total
                log_obj.imported_items = imported
                log_obj.failed_items = failed
                log_obj.completed_at = datetime.now(timezone.utc)

            return {
                "source": "github",
                "source_url": repo_url,
                "total_items": total,
                "imported_items": imported,
                "failed_items": failed,
                "status": "completed",
            }
        except Exception as e:
            await self.import_repo.update_status(
                id=log.id,
                status="failed",
                error_message=str(e),
            )
            raise BadRequestException(f"GitHub import failed: {str(e)}")

    async def import_from_file(
        self, user_id: int, file_content: str, source: str
    ) -> dict:
        total = 0
        imported = 0
        failed = 0

        try:
            data = json.loads(file_content)
            if isinstance(data, list):
                prompts_list = data
            elif isinstance(data, dict) and "prompts" in data:
                prompts_list = data["prompts"]
            else:
                prompts_list = [data]
        except json.JSONDecodeError:
            prompts_list = [{"title": f"Imported from {source}", "content": file_content}]

        total = len(prompts_list)

        log = await self.import_repo.create(
            imported_by=user_id,
            source="file",
            source_url=source,
            total_items=total,
            imported_items=0,
            failed_items=0,
            status="processing",
            started_at=datetime.now(timezone.utc),
        )

        for item in prompts_list:
            try:
                title = item.get("title", item.get("name", "Untitled"))
                content = item.get("content", item.get("prompt", item.get("text", "")))
                description = item.get("description", f"Imported from {source}")
                category_id = item.get("category_id")
                is_public = item.get("is_public", False)

                await self.prompt_repo.create(
                    user_id=user_id,
                    title=title,
                    content=content,
                    description=description,
                    category_id=category_id,
                    is_public=is_public,
                    imported_from=source,
                )
                imported += 1
            except Exception:
                failed += 1

        log_obj = await self.import_repo.get(log.id)
        if log_obj:
            log_obj.total_items = total
            log_obj.imported_items = imported
            log_obj.failed_items = failed
            log_obj.completed_at = datetime.now(timezone.utc)
            log_obj.status = "completed"

        return {
            "source": "file",
            "source_url": source,
            "total_items": total,
            "imported_items": imported,
            "failed_items": failed,
            "status": "completed",
        }

    async def import_from_api(
        self, user_id: int, source_url: str
    ) -> dict:
        log = await self.import_repo.create(
            imported_by=user_id,
            source="api",
            source_url=source_url,
            total_items=0,
            imported_items=0,
            failed_items=0,
            status="processing",
            started_at=datetime.now(timezone.utc),
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(source_url)
                resp.raise_for_status()
                data = resp.json()

            prompts_list = []
            if isinstance(data, list):
                prompts_list = data
            elif isinstance(data, dict):
                for key in ("prompts", "data", "items", "results"):
                    if key in data and isinstance(data[key], list):
                        prompts_list = data[key]
                        break
                if not prompts_list:
                    prompts_list = [data]

            total = len(prompts_list)
            imported = 0
            failed = 0

            for item in prompts_list:
                try:
                    title = item.get("title", item.get("name", "Untitled"))
                    content = item.get("content", item.get("prompt", json.dumps(item)))
                    description = item.get("description", f"Imported from {source_url}")

                    await self.prompt_repo.create(
                        user_id=user_id,
                        title=title,
                        content=content,
                        description=description,
                        imported_from=source_url,
                        is_public=False,
                    )
                    imported += 1
                except Exception:
                    failed += 1

            log_obj = await self.import_repo.get(log.id)
            if log_obj:
                log_obj.total_items = total
                log_obj.imported_items = imported
                log_obj.failed_items = failed
                log_obj.completed_at = datetime.now(timezone.utc)
                log_obj.status = "completed"

            return {
                "source": "api",
                "source_url": source_url,
                "total_items": total,
                "imported_items": imported,
                "failed_items": failed,
                "status": "completed",
            }
        except Exception as e:
            await self.import_repo.update_status(
                id=log.id,
                status="failed",
                error_message=str(e),
            )
            raise BadRequestException(f"API import failed: {str(e)}")

    async def get_import_history(
        self, user_id: int, skip: int = 0, limit: int = 20
    ) -> ImportListResponse:
        all_imports = await self.import_repo.get_by_user(user_id)
        total = len(all_imports)
        page_imports = all_imports[skip : skip + limit]

        items = [self._to_import_response(imp) for imp in page_imports]
        return ImportListResponse(
            imports=items,
            pagination={
                "total": total,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "size": limit,
                "pages": max(1, (total + limit - 1) // limit) if limit > 0 else 1,
            },
        )

    async def get_all_imports(
        self, skip: int = 0, limit: int = 20
    ) -> ImportListResponse:
        imports, total = await self.import_repo.get_multi(
            skip=skip, limit=limit, sort_field="created_at"
        )

        items = [self._to_import_response(imp) for imp in imports]
        return ImportListResponse(
            imports=items,
            pagination={
                "total": total,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "size": limit,
                "pages": max(1, (total + limit - 1) // limit) if limit > 0 else 1,
            },
        )

    def _to_import_response(self, imp: object) -> ImportResponse:
        return ImportResponse(
            id=imp.id,
            uuid=imp.uuid,
            source=imp.source,
            source_url=imp.source_url,
            total_items=imp.total_items,
            imported_items=imp.imported_items,
            failed_items=imp.failed_items,
            status=imp.status,
            error_message=imp.error_message,
            imported_by=imp.imported_by,
            started_at=imp.started_at,
            completed_at=imp.completed_at,
            created_at=imp.created_at,
        )
