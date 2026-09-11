"""
chat.py — Interactive Store Manager Chat Assistant
Zudio Store Insight Engine

Interactive terminal chat that mirrors the web AI copilot exactly:
  - AI mode (Gemini / OpenAI) when a valid API key is in .env
  - Deterministic Offline Safe Mode when no key is configured
  - Multi-turn conversation history maintained across the session
  - All 8 questions + Hindi briefing available via keyword routing
"""

import os
import sys
import textwrap
import requests
import pandas as pd

# Ensure stdout / stderr handle UTF-8 cleanly on all Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from insight_engine import DataValidator, AnalyticsEngine, DEFAULT_INPUT_PATH
from copilot import build_system_prompt, get_fallback_reply
from config import get_active_api_key


# ---------------------------------------------------------------------------
# Terminal formatting helpers
# ---------------------------------------------------------------------------

def _fmt(text: str, width: int = 72) -> str:
    """Converts markdown AI reply into clean, readable terminal text."""
    lines = text.split("\n")
    out = []
    for line in lines:
        s = line.strip()
        if not s:
            out.append("")
            continue
        if s.startswith("#"):
            out.append("")
            out.append(f"[{s.lstrip('#').replace('**', '').strip().upper()}]")
            continue
        if s in ("---", "***", "___"):
            out.append("-" * width)
            continue
        if s.startswith(("* ", "- ", "• ")):
            body = s[2:].replace("**", "").strip()
            out.append(textwrap.fill(body, width=width, initial_indent="  • ", subsequent_indent="    "))
            continue
        if len(s) > 3 and s[0].isdigit() and s[1:3] in (". ", ") "):
            prefix, body = s[:3], s[3:].replace("**", "").strip()
            out.append(textwrap.fill(body, width=width, initial_indent=f"  {prefix}", subsequent_indent="     "))
            continue
        out.append(textwrap.fill(s.replace("**", ""), width=width))
    return "\n".join(out)


def _safe_print(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        print(text.encode(enc, errors="replace").decode(enc))
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Interactive chat
# ---------------------------------------------------------------------------

def start_interactive_chat(dataset_path: str = DEFAULT_INPUT_PATH):
    """
    Launches an interactive console chat with the AI Store Copilot.
    Uses the same pipeline as the web dashboard:
      - Live Gemini/OpenAI when API key is configured in .env
      - Deterministic offline fallback when no key is present
    Multi-turn conversation history is maintained for contextual follow-ups.
    """
    if not os.path.exists(dataset_path):
        print(f"\n[!] Dataset '{dataset_path}' not found. Run 'python generate_data.py' first.\n")
        return

    # Load and validate data — identical pipeline to web dashboard
    raw_df = pd.read_csv(dataset_path)
    clean_df, _ = DataValidator.validate_and_clean(raw_df)
    metrics = AnalyticsEngine(clean_df).compute_all_metrics()

    # Build full system prompt (same one used by the web app)
    system_instruction = build_system_prompt(metrics)

    # Detect API mode for banner
    api_key, provider = get_active_api_key()
    if api_key:
        mode_label = f"AI Mode ({provider.upper()})"
        mode_note = f"Live responses via {provider.capitalize()} API."
    else:
        mode_label = "Offline Safe Mode"
        mode_note = "No API key — using Deterministic Intelligence Engine (verified CSV data)."

    print("\n" + "=" * 65)
    print(f"   * ZUDIO STORE AI COPILOT  —  {mode_label} *")
    print("=" * 65)
    print(f"  {mode_note}")
    print("  Ask anything about your September store performance.")
    print("  Try: 'q1', 'q6', 'best selling product', 'hindi mein batao',")
    print("       'next week actions', 'week on week trend', etc.")
    print("  Type 'exit' or 'q' to end the session.")
    print("-" * 65)

    # Multi-turn history (Gemini format: list of {role, parts})
    conversation_history = []

    while True:
        try:
            sys.stdout.flush()
            user_input = input("\nStore Manager > ").strip()
        except (KeyboardInterrupt, EOFError):
            _safe_print("\n\nAssistant: Goodbye! Have a great sales week.\n")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            _safe_print("\nAssistant: Goodbye! Have a great sales week.\n")
            break

        reply = None
        is_hindi = "hindi" in user_input.lower() or "सारांश" in user_input

        # ---- AI mode: try live API first ----
        if api_key:
            conversation_history.append({"role": "user", "parts": [{"text": user_input}]})

            if provider == "gemini":
                payload = {
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "contents": conversation_history,
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
                }
                for model in ("gemini-2.5-flash", "gemini-2.0-flash"):
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    try:
                        res = requests.post(url, json=payload, timeout=30)
                        if res.status_code == 200:
                            candidates = res.json().get("candidates", [])
                            if candidates:
                                reply = candidates[0]["content"]["parts"][0]["text"].strip()
                                conversation_history.append({"role": "model", "parts": [{"text": reply}]})
                                break
                        else:
                            print(f"  [warn] {model}: HTTP {res.status_code}, trying next...")
                    except Exception as e:
                        print(f"  [warn] {model}: {e}, trying next...")

            elif provider == "openai":
                # Build OpenAI-format message list from conversation history
                messages = [{"role": "system", "content": system_instruction}]
                for turn in conversation_history:
                    role = "assistant" if turn["role"] == "model" else "user"
                    messages.append({"role": role, "content": turn["parts"][0]["text"]})
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    res = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json={"model": "gpt-4o-mini", "messages": messages, "temperature": 0.3},
                        timeout=30
                    )
                    if res.status_code == 200:
                        reply = res.json()["choices"][0]["message"]["content"].strip()
                        conversation_history.append({"role": "model", "parts": [{"text": reply}]})
                    else:
                        print(f"  [warn] OpenAI: HTTP {res.status_code}")
                except Exception as e:
                    print(f"  [warn] OpenAI call failed: {e}")

        # ---- Offline / API-failed fallback ----
        if not reply:
            badge = (
                "> ⚙️ ऑफलाइन सेफ मोड: वेरिफाइड CSV डेटा\n\n"
                if is_hindi
                else "> ⚙️ Offline Safe Mode: Deterministic Intelligence Engine (Verified CSV)\n\n"
            )
            reply = badge + get_fallback_reply(user_input, metrics)

        _safe_print(f"\nAssistant >\n{_fmt(reply)}\n")
        print("-" * 65)


if __name__ == "__main__":
    start_interactive_chat()
