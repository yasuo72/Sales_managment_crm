"""
config.py — Zudio Store Operations Dashboard
Environment & API Configuration

Handles live .env reading, API key resolution, and provider detection.
Reads the .env file from disk on every call — enabling zero-restart key
switching between AI mode and Offline Safe Mode.
"""

import os
from typing import Optional, Tuple
from dotenv import dotenv_values

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_active_api_key() -> Tuple[Optional[str], Optional[str]]:
    """
    Reads live .env file directly from disk on each call.
    Filters out empty strings and template placeholder values.
    Enables instant switching between AI mode and Offline Safe Mode
    without server restart.

    Returns:
        (api_key, provider): e.g. ("AIza...", "gemini") or (None, None)
    """
    env_path = os.path.join(BASE_DIR, ".env")
    env_dict = dotenv_values(env_path) if os.path.exists(env_path) else {}

    _INVALID = {"your_gemini_api_key_here", "your_openai_api_key_here", "None", "null", ""}

    # --- Gemini ---
    g_disk = (env_dict.get("GEMINI_API_KEY") or env_dict.get("GOOGLE_API_KEY") or "").strip()
    if g_disk and g_disk not in _INVALID:
        return g_disk, "gemini"

    # Fall back to process environment for Gemini
    g_env = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if g_env and g_env not in _INVALID:
        return g_env, "gemini"

    # --- OpenAI ---
    o_disk = (env_dict.get("OPENAI_API_KEY") or "").strip()
    if o_disk and o_disk not in _INVALID:
        return o_disk, "openai"

    o_env = (os.getenv("OPENAI_API_KEY") or "").strip()
    if o_env and o_env not in _INVALID:
        return o_env, "openai"

    return None, None
