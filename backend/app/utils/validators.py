from __future__ import annotations

import re
from typing import Pattern


EMAIL_PATTERN: Pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
USERNAME_PATTERN: Pattern = re.compile(r"^[a-zA-Z0-9_]{3,30}$")
URL_PATTERN: Pattern = re.compile(
    r"^https?:\/\/([\w.-]+)+(:\d+)?(\/[\w\-._~:/?#\[\]@!$&'()*+,;=]*)?$"
)
PASSWORD_MIN_LENGTH: int = 8

DANGEROUS_TAGS: set[str] = {
    "script", "style", "iframe", "object", "embed", "applet",
    "meta", "link", "form", "input", "button", "textarea",
    "select", "option", "optgroup", "frame", "frameset",
    "noframes", "ilayer", "layer", "marquee", "video", "audio",
    "canvas", "svg", "math",
}

DANGEROUS_ATTRS: set[str] = {
    "onload", "onclick", "onerror", "onmouseover", "onfocus",
    "onblur", "onsubmit", "onchange", "onkeydown", "onkeyup",
    "onkeypress", "ondblclick", "onmousedown", "onmouseup",
    "onmousemove", "onmouseout", "onreset", "onselect",
    "onunload", "javascript:", "expression(",
}

_HTML_TAG_RE: Pattern = re.compile(r"<\/?([a-zA-Z0-9]+)[^>]*>", re.IGNORECASE | re.DOTALL)
_ATTR_RE: Pattern = re.compile(r'\s(on[a-z]+|href|src|action|formaction)\s*=\s*("[^"]*"|\'[^\']*\'|[^\s>]+)', re.IGNORECASE)


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))


def validate_password(password: str) -> tuple[bool, str]:
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'\/~`]", password):
        return False, "Password must contain at least one special character"
    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 30:
        return False, "Username must not exceed 30 characters"
    if not USERNAME_PATTERN.match(username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


def validate_url(url: str) -> bool:
    return bool(URL_PATTERN.match(url))


def sanitize_html(text: str) -> str:
    def _replace_tag(match: re.Match) -> str:
        tag_name = match.group(1).lower()
        if tag_name in DANGEROUS_TAGS:
            return ""
        full_tag = match.group(0)
        cleaned = _ATTR_RE.sub("", full_tag)
        return cleaned

    cleaned = _HTML_TAG_RE.sub(_replace_tag, text)
    for attr in DANGEROUS_ATTRS:
        cleaned = cleaned.lower().replace(attr, "")
    return cleaned


def truncate_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."
