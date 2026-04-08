from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# ═══════════════════════════════════════════════════
# 🚫 LEVEL 1 — BLOCKED: These NEVER execute, period
# ═══════════════════════════════════════════════════
BLOCKED_COMMANDS = [
    # Disk destruction
    "format",
    "diskpart",

    # Boot / recovery tampering
    "bcdedit",
    "bootrec",
    "bootcfg",

    # Registry destruction
    "reg delete",
    "regedit",
    "regsvr32",

    # System file tampering
    "sfc /scannow",
    "dism",
    "takeown",
    "icacls",

    # Ransomware-like
    "cipher /w",
    "vssadmin delete",

    # Remote access abuse
    "netsh advfirewall set allprofiles state off",
    "net user administrator",

    # Self-replication / fork bomb patterns
    "start cmd /k",
    "%0",
]

# ═══════════════════════════════════════════════════════════════
# ⚠️  LEVEL 2 — DANGEROUS: These run ONLY after YES confirmation
# ═══════════════════════════════════════════════════════════════
DANGEROUS_COMMANDS = [
    # File deletion
    "del",
    "erase",
    "rmdir",
    "rd ",

    # Process killing
    "taskkill",
    "tskill",

    # Power actions
    "shutdown",
    "restart",
    "logoff",
    "wmic",

    # Network changes
    "netsh",
    "net stop",
    "net start",
    "ipconfig /release",
    "ipconfig /flushdns",

    # Privilege escalation
    "runas",
    "psexec",

    # Scheduled tasks
    "schtasks /delete",
    "schtasks /create",

    # Environment tampering
    "setx",
    "attrib +h",
    "attrib -h",
]

# ═══════════════════════════════════════════════════════════════
# 🧠 LEVEL 3 — SUSPICIOUS PATTERNS (regex-style keyword checks)
# ═══════════════════════════════════════════════════════════════
SUSPICIOUS_PATTERNS = [
    "rm -rf",           # Unix-style but still flag it
    "drop table",       # SQL injection attempt
    "exec(",            # Code execution attempt
    "eval(",
    "powershell -enc",  # Encoded PS commands (malware tactic)
    "invoke-expression",
    "wget http",        # Downloading executables
    "curl http",
    "certutil -decode", # Malware delivery tactic
    "> c:\\windows",    # Writing to system directory
    ">> c:\\windows",
    "c:\\system32",
]


# ═══════════════════════════════════════════════════
# 🔍 CORE VALIDATION FUNCTION
# ═══════════════════════════════════════════════════

def check_command(command: str) -> dict:
    """
    Validate a command through all 3 safety levels.

    Returns:
        {
            "allowed"  : bool,
            "level"    : "safe" | "dangerous" | "blocked" | "suspicious",
            "reason"   : str,
            "matched"  : str   (which keyword triggered)
        }
    """
    cmd_lower = command.lower().strip()

    # --- Level 1: Hard blocked ---
    for blocked in BLOCKED_COMMANDS:
        if blocked.lower() in cmd_lower:
            return {
                "allowed" : False,
                "level"   : "blocked",
                "reason"  : "This command is permanently blocked for system safety.",
                "matched" : blocked
            }

    # --- Level 3: Suspicious patterns ---
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern.lower() in cmd_lower:
            return {
                "allowed" : False,
                "level"   : "suspicious",
                "reason"  : "Suspicious pattern detected. This looks like it could be malicious.",
                "matched" : pattern
            }

    # --- Level 2: Dangerous (needs confirmation) ---
    for danger in DANGEROUS_COMMANDS:
        if danger.lower() in cmd_lower:
            return {
                "allowed" : True,           # allowed BUT needs confirm
                "level"   : "dangerous",
                "reason"  : "This command can cause irreversible changes to your system.",
                "matched" : danger
            }

    # --- All clear ---
    return {
        "allowed" : True,
        "level"   : "safe",
        "reason"  : "",
        "matched" : ""
    }


# ═══════════════════════════════════════════════════
# 🖥️  DISPLAY FUNCTIONS
# ═══════════════════════════════════════════════════

def show_blocked_warning(command: str, result: dict):
    """Show a hard block message — red, no option to proceed."""
    
    icon = "🚫" if result["level"] == "blocked" else "🧠"
    title_color = "red" if result["level"] == "blocked" else "magenta"
    label = "BLOCKED" if result["level"] == "blocked" else "SUSPICIOUS"

    console.print()
    console.print(Panel(
        f"[bold {title_color}]{icon}  Command {label}[/bold {title_color}]\n\n"
        f"[white]Command :[/white]  [red]{command}[/red]\n"
        f"[white]Trigger :[/white]  [yellow]{result['matched']}[/yellow]\n"
        f"[white]Reason  :[/white]  {result['reason']}\n\n"
        f"[dim]This command was [bold]NOT executed[/bold] and cannot be run through CmdBot.[/dim]",
        border_style=title_color,
        title=f"[bold {title_color}]Safety Block — Level {'1' if result['level'] == 'blocked' else '3'}[/bold {title_color}]"
    ))
    console.print()


def show_dangerous_warning(command: str, result: dict) -> bool:
    """
    Show a yellow confirmation prompt for dangerous commands.
    Returns True if user confirms with YES, False otherwise.
    """
    console.print()
    console.print(Panel(
        f"[bold yellow]⚠️   DANGEROUS COMMAND DETECTED[/bold yellow]\n\n"
        f"[white]Command :[/white]  [red]{command}[/red]\n"
        f"[white]Trigger :[/white]  [yellow]{result['matched']}[/yellow]\n"
        f"[white]Reason  :[/white]  {result['reason']}\n\n"
        f"[dim]This action [bold]may be irreversible[/bold]. Proceed with caution.[/dim]",
        border_style="yellow",
        title="[bold yellow]⚠️  Safety Warning — Level 2[/bold yellow]"
    ))

    console.print("[bold yellow]  Type [green]YES[/green] to confirm, or anything else to cancel:[/bold yellow] ", end="")
    answer = input("").strip()

    if answer == "YES":
        console.print("[dim green]  ✅ Confirmed. Executing...[/dim green]\n")
        return True
    else:
        console.print("[dim red]  ❌ Cancelled. Command was not executed.[/dim red]\n")
        return False


def show_safety_levels():
    """Print a summary table of all safety rules — triggered by 'cmdbot help safety'."""
    
    table = Table(title="🛡️  CmdBot Safety Levels", border_style="cyan")
    table.add_column("Level", style="bold cyan", width=8)
    table.add_column("Type",  style="bold white", width=14)
    table.add_column("Action", style="bold", width=18)
    table.add_column("Examples", style="dim")

    table.add_row("1", "🚫 Blocked",    "[red]Never executes[/red]",      "format, diskpart, bcdedit, reg delete")
    table.add_row("2", "⚠️  Dangerous", "[yellow]Needs YES confirm[/yellow]", "del, rmdir, shutdown, taskkill")
    table.add_row("3", "🧠 Suspicious", "[magenta]Always blocked[/magenta]",   "powershell -enc, certutil, curl http")
    table.add_row("✅", "Safe",         "[green]Runs immediately[/green]",  "dir, echo, ipconfig, type, cd")

    console.print()
    console.print(table)
    console.print()