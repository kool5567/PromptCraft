from __future__ import annotations

import base64
import re
from typing import Any, Optional

import httpx

from app.core.config import settings

GITHUB_API_BASE = "https://api.github.com"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
PROMPT_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml"}
PROMPT_KEYWORDS = ["prompt", "template", "prompt-template", "ai-prompt"]


class GitHubClient:
    def __init__(self) -> None:
        self.base_url = GITHUB_API_BASE
        self.token = settings.github_access_token
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PromptCraft/1.0",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        repo_url = repo_url.rstrip("/")
        if repo_url.startswith("https://github.com/"):
            parts = repo_url.replace("https://github.com/", "").split("/")
        elif repo_url.startswith("git@github.com:"):
            parts = repo_url.replace("git@github.com:", "").split("/")
        else:
            raise ValueError(f"Unsupported GitHub URL format: {repo_url}")

        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {repo_url}")

        owner = parts[0]
        repo = parts[1].replace(".git", "")
        return owner, repo

    async def _make_request(self, url: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30.0)
            if response.status_code == 403:
                raise PermissionError("GitHub API rate limit exceeded or access denied")
            if response.status_code == 404:
                raise FileNotFoundError(f"Resource not found: {url}")
            response.raise_for_status()
            return response.json()

    async def _make_raw_request(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"User-Agent": "PromptCraft/1.0"}, timeout=30.0)
            response.raise_for_status()
            return response.text

    async def _get_download_url(self, owner: str, repo: str, path: str) -> str:
        return f"{GITHUB_RAW_BASE}/{owner}/{repo}/main/{path}"

    def _is_prompt_file(self, filename: str) -> bool:
        ext = re.search(r"(\.[a-zA-Z0-9]+)$", filename)
        if not ext:
            return False
        return ext.group(1).lower() in PROMPT_EXTENSIONS

    def _is_prompt_content(self, text: str) -> bool:
        if not text or len(text.strip()) < 20:
            return False
        lower = text.lower()
        keywords_found = sum(1 for kw in PROMPT_KEYWORDS if kw in lower)
        return keywords_found >= 1

    def _parse_prompt_metadata(self, filename: str, content: str) -> dict[str, Any]:
        title = filename.replace(".md", "").replace(".txt", "").replace(".json", "").replace(".yaml", "").replace(".yml", "")
        title = title.replace("-", " ").replace("_", " ").title()
        description = ""
        content_body = content
        variables: list[str] = []

        lines = content.splitlines()
        if lines and lines[0].startswith("# "):
            title = lines[0].lstrip("# ").strip()
            content_body = "\n".join(lines[1:]).strip()
        elif lines and lines[0].startswith("---"):
            try:
                end_idx = content.find("---", 3)
                if end_idx != -1:
                    front_matter = content[3:end_idx].strip()
                    content_body = content[end_idx + 3:].strip()
                    for line in front_matter.splitlines():
                        if ":" in line:
                            key, val = line.split(":", 1)
                            if key.strip().lower() == "title":
                                title = val.strip().strip("\"'")
                            elif key.strip().lower() == "description":
                                description = val.strip().strip("\"'")
            except Exception:
                pass

        var_pattern = re.compile(r"\{\{(\w+)\}\}")
        variables = list(set(var_pattern.findall(content_body)))

        return {
            "title": title,
            "description": description,
            "content": content_body,
            "variables": variables if variables else None,
            "source_filename": filename,
        }

    async def get_repo_contents(self, repo_url: str, path: str = "") -> list[dict[str, Any]]:
        owner, repo = await self._parse_repo_url(repo_url)
        api_path = f"/repos/{owner}/{repo}/contents/{path}".rstrip("/")
        url = f"{self.base_url}{api_path}"
        data = await self._make_request(url)

        if isinstance(data, dict):
            data = [data]
        return data

    async def get_file_content(self, repo_url: str, file_path: str) -> str:
        owner, repo = await self._parse_repo_url(repo_url)
        api_path = f"/repos/{owner}/{repo}/contents/{file_path}"
        url = f"{self.base_url}{api_path}"
        data = await self._make_request(url)

        if isinstance(data, dict) and data.get("encoding") == "base64" and data.get("content"):
            decoded = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return decoded

        raw_url = await self._get_download_url(owner, repo, file_path)
        return await self._make_raw_request(raw_url)

    async def search_prompts(self, query: str, page: int = 1) -> list[dict[str, Any]]:
        search_query = f"{query}+language:markdown+language:yaml+language:json"
        url = f"{self.base_url}/search/repositories?q={search_query}&sort=stars&order=desc&per_page=30&page={page}"
        data = await self._make_request(url)
        return data.get("items", [])

    async def get_trending_prompts(self) -> list[dict[str, Any]]:
        query = "prompt+template+stars:>10"
        url = f"{self.base_url}/search/repositories?q={query}&sort=stars&order=desc&per_page=10"
        data = await self._make_request(url)
        return data.get("items", [])

    async def import_from_repo(self, repo_url: str) -> list[dict[str, Any]]:
        owner, repo = await self._parse_repo_url(repo_url)
        default_branch = "main"

        try:
            branch_url = f"{self.base_url}/repos/{owner}/{repo}"
            branch_data = await self._make_request(branch_url)
            default_branch = branch_data.get("default_branch", "main")
        except Exception:
            pass

        results: list[dict[str, Any]] = []
        contents = await self._list_all_files(owner, repo, default_branch)

        for item in contents:
            if item.get("type") != "file":
                continue
            name: str = item.get("name", "")
            if not self._is_prompt_file(name):
                continue

            try:
                raw_url = f"{GITHUB_RAW_BASE}/{owner}/{repo}/{default_branch}/{item['path']}"
                content = await self._make_raw_request(raw_url)
                if not self._is_prompt_content(content):
                    continue
                parsed = self._parse_prompt_metadata(name, content)
                parsed["source_url"] = f"https://github.com/{owner}/{repo}/blob/{default_branch}/{item['path']}"
                parsed["repo"] = f"{owner}/{repo}"
                results.append(parsed)
            except Exception:
                continue

        return results

    async def _list_all_files(
        self, owner: str, repo: str, branch: str, path: str = ""
    ) -> list[dict[str, Any]]:
        contents = await self.get_repo_contents(f"https://github.com/{owner}/{repo}", path)
        files: list[dict[str, Any]] = []

        for item in contents:
            if item.get("type") == "file":
                files.append(item)
            elif item.get("type") == "dir":
                try:
                    sub_files = await self._list_all_files(owner, repo, branch, item.get("path", ""))
                    files.extend(sub_files)
                except Exception:
                    continue

        return files
