"""Single source of truth for every filesystem path in the project.

The Docker/source layout keeps all state under ``<repo>/data``. Desktop builds
can override the immutable resource root and writable data root through
environment variables set by ``desktop.main``.
"""
import os


def _absolute_env(name: str, default: str) -> str:
    value = os.environ.get(name, "").strip()
    return os.path.abspath(os.path.expanduser(value or default))


_SOURCE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = _absolute_env("DOUYIN_CHAT_RESOURCE_DIR", _SOURCE_ROOT)
DATA_DIR = _absolute_env("DOUYIN_CHAT_DATA_DIR", os.path.join(REPO_ROOT, "data"))

# Databases / config
DB_PATH = os.path.join(DATA_DIR, "chat.db")
CONFIG_PATH = os.path.join(DATA_DIR, "panel_config.json")

# Logs & discovery artifacts
SCRAPE_LOG = os.path.join(DATA_DIR, "scrape.log")
DISCOVER_LOG = os.path.join(DATA_DIR, "discover.log")
CONVERSATIONS_LIST = os.path.join(DATA_DIR, "conversations_list.json")

# Browser profile (the persistent Chromium context that *is* the login state)
BROWSER_PROFILE = os.path.join(DATA_DIR, "browser_profile")

# Media tree
MEDIA_DIR = os.path.join(DATA_DIR, "media")
IMAGES_DIR = os.path.join(MEDIA_DIR, "images")
EMOJI_DIR = os.path.join(MEDIA_DIR, "emoji")
VOICE_DIR = os.path.join(MEDIA_DIR, "voice")
AVATARS_DIR = os.path.join(MEDIA_DIR, "avatars")
VIDEOS_DIR = os.path.join(MEDIA_DIR, "videos")

# Frontend build output served by the backend
FRONTEND_DIST = _absolute_env(
    "DOUYIN_CHAT_FRONTEND_DIST",
    os.path.join(REPO_ROOT, "frontend", "dist"),
)
