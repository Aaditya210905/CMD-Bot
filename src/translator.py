import os
from pathlib import Path
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from src.logger import log_translation, log_error, log_clarification_question

load_dotenv()
console = Console()

# ── Init OpenAI client ─────────────────────────────────────────
client = OpenAI(
  base_url="http://localhost:11434/v1",
  api_key="ollama"
)

PROMPT_FILE_TRANSLATION = Path(__file__).with_name("system_prompt_translation.txt")
PROMPT_FILE_CLASSIFIER   = Path(__file__).with_name("system_prompt_classifier.txt")
TRANSLATION_MODEL = os.getenv("OPENROUTER_TRANSLATION_MODEL", "gemma4:e4b")
CLASSIFIER_MODEL = os.getenv("OPENROUTER_CLASSIFIER_MODEL", TRANSLATION_MODEL)

QUESTION_STARTERS = {
    "what",
    "which",
    "where",
    "when",
    "why",
    "how",
    "do",
    "does",
    "did",
    "is",
    "are",
    "can",
    "could",
    "would",
    "should",
    "will",
    "who",
    "whom",
    "whose",
}


def load_system_prompt(PROMPT_FILE) -> str:
    """Load the system prompt from disk so it can be edited separately."""
    try:
        return PROMPT_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        console.print(f"[bold red]  ❌ Prompt file not found: {PROMPT_FILE}[/bold red]\n")
    except Exception as e:
        console.print(f"[bold red]  ❌ Failed to load prompt file: {e}[/bold red]\n")
    return ""


# ══════════════════════════════════════════════════════════════
# 🔧 HELPER — Strip any accidental formatting from AI output
# ══════════════════════════════════════════════════════════════
def clean_command(raw: str) -> str:
    """
    Remove markdown, backticks, extra whitespace, or
    code fences that LLM might accidentally include.
    """
    cleaned = raw.strip()

    # Remove code fences like ```cmd ... ``` or ```...```
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Drop first and last fence lines
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    # Remove stray backticks
    cleaned = cleaned.replace("`", "")

    # Remove wrapping quotes if LLM added them
    if (cleaned.startswith('"') and cleaned.endswith('"')) or \
       (cleaned.startswith("'") and cleaned.endswith("'")):
        cleaned = cleaned[1:-1].strip()

    return cleaned.strip()


def looks_like_question(text: str) -> bool:
    """Heuristic fallback when the classifier model is unavailable."""
    stripped = text.strip()
    if not stripped:
        return False

    if stripped.endswith("?") and not stripped.endswith("/?"):
        return True

    first_word = stripped.split(maxsplit=1)[0].strip("\"'.,:;!()").lower()
    return first_word in QUESTION_STARTERS


def classify_output_kind(user_input: str, llm_output: str) -> str:
    """Second LLM layer to classify output as CMD command or clarification question."""
    classifier_prompt = load_system_prompt(PROMPT_FILE_CLASSIFIER)

    try:
        response = client.chat.completions.create(
            model=CLASSIFIER_MODEL,
            messages=[
                {"role": "system", "content": classifier_prompt},
                {
                    "role": "user",
                    "content": (
                        f"User input: {user_input}\n"
                        f"Assistant output: {llm_output}\n"
                        "Label:"
                    ),
                },
            ],
            temperature=0,
            max_tokens=5,
        )

        verdict = (response.choices[0].message.content or "").strip().upper()
        if "QUESTION" in verdict:
            return "question"
        if "COMMAND" in verdict:
            return "command"
    except Exception as e:
        console.print(
            f"[yellow]  ⚠️  Output classifier failed: {e}. Falling back to heuristic.[/yellow]"
        )

    return "question" if looks_like_question(llm_output) else "command"


# ══════════════════════════════════════════════════════════════
# 🚀 MAIN TRANSLATE FUNCTION
# ══════════════════════════════════════════════════════════════
def translate(user_input: str, history: Optional[list] = None) -> dict:
    """
    Send natural language to LLM and return the CMD command.

    Args:
        user_input : Plain English instruction from user
        history    : Past conversation turns for context

    Returns:
        {
            "success"  : bool,
            "kind"     : str,   ← command | clarification | error
            "command"  : str,   ← the CMD command to run
            "question" : str,   ← clarification question if needed
            "raw"      : str,   ← raw LLM response before cleaning
            "error"    : str    ← error message if failed
        }
    """

    if history is None:
        history = []

    # Build messages — system prompt + history + new user input
    system_prompt = load_system_prompt(PROMPT_FILE_TRANSLATION)
    if not system_prompt:
        log_translation(user_input, "", False, "Failed to load system prompt.")
        return {
            "success": False,
            "kind": "error",
            "command": "",
            "question": "",
            "raw": "",
            "error": "System prompt file is missing or unreadable."
        }

    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": user_input})

    console.print(f"[dim]  🤖 Translating:[/dim] [italic white]{user_input}[/italic white]")

    try:
        response = client.chat.completions.create(
            model=TRANSLATION_MODEL,     # Fast, cheap, accurate
            messages=messages,
            temperature=0,             # 0 = deterministic, consistent output
            max_tokens=100,            # Commands are short — no need for more
        )

        raw = (response.choices[0].message.content or "").strip()
        output = clean_command(raw)

        # LLM signals it can't do this via CMD
        if output.upper() == "CANNOT_EXECUTE":
            console.print("[yellow]  ⚠️  LLM couldn't find a CMD equivalent for that.[/yellow]\n")
            log_translation(user_input, "", False, "LLM indicated no CMD equivalent.")
            return {
                "success": False,
                "kind": "error",
                "command": "",
                "question": "",
                "raw": raw,
                "error": "No CMD equivalent found.",
            }

        # Empty response guard
        if not output:
            console.print("[yellow]  ⚠️  LLM returned an empty response.[/yellow]\n")
            log_translation(user_input, "", False, "LLM returned an empty response.")
            return {
                "success": False,
                "kind": "error",
                "command": "",
                "question": "",
                "raw": raw,
                "error": "Empty response from LLM.",
            }

        output_kind = classify_output_kind(user_input, output)
        if output_kind == "question":
            console.print(f"[yellow]  ❓ Clarification needed:[/yellow] [italic white]{output}[/italic white]\n")
            log_translation(user_input, output, False, "LLM needs clarification.")
            log_clarification_question(user_input, output)
            return {
                "success": False,
                "kind": "clarification",
                "command": "",
                "question": output,
                "raw": raw,
                "error": "",
            }

        console.print(f"[dim]  🔁 Translated to:[/dim] [bold cyan]{output}[/bold cyan]\n")
        log_translation(user_input, output, True, "Translation successful.")
        return {
            "success": True,
            "kind": "command",
            "command": output,
            "question": "",
            "raw": raw,
            "error": "",
        }

    except Exception as e:
        console.print(f"[bold red]  ❌ LLM Error: {e}[/bold red]\n")
        log_translation(user_input, "", False, f"LLM Error: {e}")
        return {
            "success": False,
            "kind": "error",
            "command": "",
            "question": "",
            "raw": "",
            "error": str(e),
        }