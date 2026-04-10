import os
import json
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
console = Console()

# ── Debug mode toggle — set DEBUG=true in .env to enable ──────
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

# ── Log file path — new file per session ──────────────────────
LOG_DIR  = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

SESSION_TIME  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE_TXT  = os.path.join(LOG_DIR, f"session_{SESSION_TIME}.log")
LOG_FILE_JSON = os.path.join(LOG_DIR, f"session_{SESSION_TIME}.json")

# ── Python standard logger (writes plain text .log) ───────────
logging.basicConfig(
    filename=LOG_FILE_TXT,
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_logger = logging.getLogger("cmdbot")

# ── JSON log — stores structured records ──────────────────────
json_log_entries = []


# ══════════════════════════════════════════════════════════════
# 🔧 CORE LOGGING FUNCTIONS
# ══════════════════════════════════════════════════════════════

def _write_json():
    """Write all entries to the JSON log file."""
    with open(LOG_FILE_JSON, "w", encoding="utf-8") as f:
        json.dump(json_log_entries, f, indent=2, ensure_ascii=False)


def log_input(user_input: str):
    """Log what the user typed."""
    file_logger.info(f"USER INPUT    | {user_input}")

    entry = {
        "timestamp" : datetime.now().isoformat(),
        "type"      : "user_input",
        "content"   : user_input,
    }
    json_log_entries.append(entry)
    _write_json()

    if DEBUG_MODE:
        console.print(Panel(
            f"[white]{user_input}[/white]",
            title="[bold blue]🐛 DEBUG — User Input[/bold blue]",
            border_style="blue"
        ))


def log_translation(user_input: str, command: str, success: bool, error: str = ""):
    """Log the AI translation result."""
    status = "SUCCESS" if success else "FAILED"
    file_logger.info(f"TRANSLATION   | {status} | Input: {user_input!r} → Command: {command!r}")
    if error:
        file_logger.warning(f"TRANS ERROR   | {error}")

    entry = {
        "timestamp"  : datetime.now().isoformat(),
        "type"       : "translation",
        "input"      : user_input,
        "command"    : command,
        "success"    : success,
        "error"      : error,
    }
    json_log_entries.append(entry)
    _write_json()

    if DEBUG_MODE:
        color = "green" if success else "red"
        console.print(Panel(
            f"[white]Input  :[/white]  [italic]{user_input}[/italic]\n"
            f"[white]Command:[/white]  [bold cyan]{command or 'N/A'}[/bold cyan]\n"
            f"[white]Status :[/white]  [{color}]{status}[/{color}]"
            + (f"\n[white]Error  :[/white]  [red]{error}[/red]" if error else ""),
            title="[bold blue]🐛 DEBUG — AI Translation[/bold blue]",
            border_style="blue"
        ))


def log_clarification_question(user_input: str, question: str):
    """Log when the assistant asks a clarification question."""
    file_logger.info(
        f"CLARIFICATION  | Input: {user_input!r} | Question: {question!r}"
    )

    entry = {
        "timestamp" : datetime.now().isoformat(),
        "type"      : "clarification_question",
        "input"     : user_input,
        "question"  : question,
    }
    json_log_entries.append(entry)
    _write_json()

    if DEBUG_MODE:
        console.print(Panel(
            f"[white]Input   :[/white]  [italic]{user_input}[/italic]\n"
            f"[white]Question:[/white]  [yellow]{question}[/yellow]",
            title="[bold blue]🐛 DEBUG — Clarification[/bold blue]",
            border_style="blue"
        ))


def log_safety(command: str, level: str, allowed: bool, matched: str = ""):
    """Log the safety check result."""
    status = "ALLOWED" if allowed else "BLOCKED"
    file_logger.info(f"SAFETY CHECK  | {status} | Level: {level} | Command: {command!r} | Matched: {matched!r}")

    entry = {
        "timestamp" : datetime.now().isoformat(),
        "type"      : "safety_check",
        "command"   : command,
        "level"     : level,
        "allowed"   : allowed,
        "matched"   : matched,
    }
    json_log_entries.append(entry)
    _write_json()

    if DEBUG_MODE:
        color = "green" if allowed else "red"
        console.print(Panel(
            f"[white]Command:[/white]  [cyan]{command}[/cyan]\n"
            f"[white]Level  :[/white]  {level}\n"
            f"[white]Status :[/white]  [{color}]{status}[/{color}]"
            + (f"\n[white]Matched:[/white]  [yellow]{matched}[/yellow]" if matched else ""),
            title="[bold blue]🐛 DEBUG — Safety Check[/bold blue]",
            border_style="blue"
        ))


def log_execution(command: str, success: bool, output: str, error: str, returncode: int):
    """Log the execution result."""
    status = "SUCCESS" if success else "FAILED"
    file_logger.info(f"EXECUTION     | {status} | Code: {returncode} | Command: {command!r}")
    if output:
        file_logger.debug(f"EXEC OUTPUT   | {output[:300]}")   # Cap at 300 chars
    if error:
        file_logger.warning(f"EXEC ERROR    | {error[:300]}")

    entry = {
        "timestamp"  : datetime.now().isoformat(),
        "type"       : "execution",
        "command"    : command,
        "success"    : success,
        "returncode" : returncode,
        "output"     : output[:500],    # Cap stored output
        "error"      : error[:500],
    }
    json_log_entries.append(entry)
    _write_json()

    if DEBUG_MODE:
        color = "green" if success else "red"
        console.print(Panel(
            f"[white]Command :[/white]  [cyan]{command}[/cyan]\n"
            f"[white]Status  :[/white]  [{color}]{status}[/{color}]\n"
            f"[white]ExitCode:[/white]  {returncode}"
            + (f"\n[white]Output  :[/white]  [dim]{output[:200]}[/dim]" if output else "")
            + (f"\n[white]Error   :[/white]  [red]{error[:200]}[/red]" if error else ""),
            title="[bold blue]🐛 DEBUG — Execution Result[/bold blue]",
            border_style="blue"
        ))


def log_session_start():
    """Log session start with system info."""
    file_logger.info("=" * 60)
    file_logger.info(f"SESSION START  | {SESSION_TIME}")
    file_logger.info(f"DEBUG MODE     | {DEBUG_MODE}")
    file_logger.info(f"LOG FILE       | {LOG_FILE_TXT}")
    file_logger.info("=" * 60)

    if DEBUG_MODE:
        console.print(f"[bold blue]🐛 Debug mode ON[/bold blue] — logs: [dim]{LOG_FILE_TXT}[/dim]\n")


def log_session_end(total_commands: int):
    """Log clean session end."""
    file_logger.info(f"SESSION END    | Total commands run: {total_commands}")
    file_logger.info("=" * 60)


def log_error(context: str, error: str):
    """Log any unexpected errors."""
    file_logger.error(f"ERROR         | {context} | {error}")

    entry = {
        "timestamp" : datetime.now().isoformat(),
        "type"      : "error",
        "context"   : context,
        "error"     : error,
    }
    json_log_entries.append(entry)
    _write_json()

    if DEBUG_MODE:
        console.print(Panel(
            f"[white]Context:[/white] {context}\n"
            f"[red]{error}[/red]",
            title="[bold red]🐛 DEBUG — Error[/bold red]",
            border_style="red"
        ))


# ══════════════════════════════════════════════════════════════
# 📋 SHOW LOG SUMMARY — triggered by 'cmdbot > show logs'
# ══════════════════════════════════════════════════════════════

def show_session_summary():
    """Print a live summary table of this session's activity."""

    inputs      = [e for e in json_log_entries if e["type"] == "user_input"]
    translations= [e for e in json_log_entries if e["type"] == "translation"]
    clarifications = [e for e in json_log_entries if e["type"] == "clarification_question"]
    executions  = [e for e in json_log_entries if e["type"] == "execution"]
    blocked     = [e for e in json_log_entries if e["type"] == "safety_check" and not e["allowed"]]
    errors      = [e for e in json_log_entries if e["type"] == "error"]

    success_execs = [e for e in executions if e["success"]]

    # ── Summary panel ──
    console.print()
    console.print(Panel(
        f"[white]Session Start :[/white]  [cyan]{SESSION_TIME}[/cyan]\n"
        f"[white]Log File (txt):[/white]  [dim]{LOG_FILE_TXT}[/dim]\n"
        f"[white]Log File (json):[/white] [dim]{LOG_FILE_JSON}[/dim]",
        title="[bold cyan]📋 Session Info[/bold cyan]",
        border_style="cyan"
    ))

    # ── Stats table ──
    table = Table(title="📊 Session Statistics", border_style="cyan")
    table.add_column("Metric",  style="bold white", width=28)
    table.add_column("Count",   style="bold cyan",  width=8)
    table.add_column("Status",  style="bold",       width=16)

    table.add_row("User Inputs",          str(len(inputs)),                   "[green]✅[/green]")
    table.add_row("AI Translations",      str(len(translations)),             "[green]✅[/green]")
    table.add_row("Clarification Questions", str(len(clarifications)),        "[yellow]❓[/yellow]" if clarifications else "[green]✅[/green]")
    table.add_row("Commands Executed",    str(len(executions)),               "[green]✅[/green]")
    table.add_row("Successful Executions",str(len(success_execs)),            "[green]✅[/green]")
    table.add_row("Failed Executions",    str(len(executions)-len(success_execs)), "[red]❌[/red]" if (len(executions)-len(success_execs)) > 0 else "[green]✅[/green]")
    table.add_row("Blocked Commands",     str(len(blocked)),                  "[yellow]⚠️[/yellow]"  if blocked else "[green]✅[/green]")
    table.add_row("Errors",               str(len(errors)),                   "[red]❌[/red]"   if errors  else "[green]✅[/green]")

    console.print(table)

    # ── Recent commands ──
    if executions:
        console.print()
        recent = Table(title="🕘 Recent Commands", border_style="dim")
        recent.add_column("Time",    style="dim",         width=10)
        recent.add_column("Command", style="cyan",        width=36)
        recent.add_column("Result",  style="bold",        width=10)

        for e in executions[-5:]:       # Show last 5
            time_str = e["timestamp"][11:19]
            result   = "[green]✅[/green]" if e["success"] else "[red]❌[/red]"
            recent.add_row(time_str, e["command"], result)

        console.print(recent)

    console.print()