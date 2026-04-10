# src/help.py

from rich.console import Console
from rich.panel   import Panel
from rich.table   import Table
from rich.columns import Columns
from rich.text    import Text

console = Console()


def show_help(topic: str = ""):
    """
    Show help content based on topic.
    'help'          → full overview
    'help safety'   → safety rules
    'help examples' → usage examples
    'help commands' → built-in commands
    """
    topic = topic.strip().lower()

    if topic in ["", "general", "help"]:
        _show_general_help()
    elif topic in ["safety"]:
        _show_safety_help()
    elif topic in ["examples", "example"]:
        _show_examples()
    elif topic in ["commands", "command"]:
        _show_commands()
    else:
        console.print(f"[yellow]  Unknown help topic '[white]{topic}[/white]'. "
                      f"Try: help, help safety, help examples, help commands[/yellow]\n")


# ══════════════════════════════════════════════════════════════
def _show_general_help():
    console.print()
    console.print(Panel(
        "[bold cyan]🤖 CmdBot — Natural Language to Windows CMD[/bold cyan]\n\n"
        "[white]Just type what you want to do in plain English.\n"
        "CmdBot uses AI to translate it into the right Windows command,\n"
        "checks it for safety, executes it, and shows you the output.[/white]\n\n"
        "[dim]Type [bold]help commands[/bold] — built-in commands list\n"
        "Type [bold]help examples[/bold] — usage examples\n"
        "Type [bold]help safety[/bold]   — safety rules explained[/dim]",
        border_style="cyan",
        title="[bold cyan]📖 CmdBot Help[/bold cyan]"
    ))

    table = Table(border_style="cyan", show_header=True)
    table.add_column("Feature",       style="bold white",  width=22)
    table.add_column("Description",   style="white",       width=42)

    table.add_row("🧠 AI Translation",    "Plain English → Windows CMD via GPT-4o-mini")
    table.add_row("🛡️  3-Level Safety",   "Blocks, warns, or confirms dangerous commands")
    table.add_row("📁 Context Tracking",  "Knows your directory, last command, last output")
    table.add_row("🔗 Multi-Step Tasks",  "Track complex operations across many commands")
    table.add_row("📋 Session Logging",   "Every action logged to logs/ as .log and .json")
    table.add_row("🐛 Debug Mode",        "Set DEBUG=true in .env for verbose output")
    table.add_row("⬆️  Arrow History",    "↑ ↓ arrows scroll through past commands")
    table.add_row("🔤 Autocomplete",      "Tab key completes commands and phrases")

    console.print(table)
    console.print()


# ══════════════════════════════════════════════════════════════
def _show_commands():
    console.print()
    table = Table(
        title="⌨️  Built-in CmdBot Commands",
        border_style="cyan"
    )
    table.add_column("Command",        style="bold cyan",  width=22)
    table.add_column("What it does",   style="white",      width=44)

    table.add_row("exit / quit / bye",   "Shut down CmdBot cleanly")
    table.add_row("help",                "Show this general help screen")
    table.add_row("help safety",         "Explain the 3 safety levels")
    table.add_row("help examples",       "Show natural language examples")
    table.add_row("help commands",       "Show this command list")
    table.add_row("show logs",           "Session statistics and recent commands")
    table.add_row("show context",        "Current directory, state, history table")
    table.add_row("start task: [name]",  "Begin tracking a multi-step task")
    table.add_row("end task",            "End task tracking and show summary")
    table.add_row("clear",               "Clear the terminal screen")

    console.print(table)
    console.print()


# ══════════════════════════════════════════════════════════════
def _show_examples():
    console.print()
    console.print(Panel(
        "[bold white]💡 Just type naturally — CmdBot understands you![/bold white]",
        border_style="cyan"
    ))

    categories = [
        ("📁 Files & Folders", [
            ("show all files",                        "dir"),
            ("show all files including hidden",        "dir /a"),
            ("make a folder called myproject",         "mkdir myproject"),
            ("delete the file called old.txt",         "del old.txt"),
            ("copy notes.txt to backup.txt",           "copy notes.txt backup.txt"),
            ("rename report.txt to final.txt",         "ren report.txt final.txt"),
            ("find all pdf files here",                "dir *.pdf"),
        ]),
        ("🌐 Network", [
            ("show my ip address",                    "ipconfig"),
            ("check if google is reachable",           "ping google.com"),
            ("show all open network connections",      "netstat -an"),
            ("flush dns cache",                        "ipconfig /flushdns"),
        ]),
        ("⚙️  System", [
            ("show running processes",                "tasklist"),
            ("show system information",               "systeminfo"),
            ("show disk space",                       "wmic logicaldisk get size,freespace,caption"),
            ("what is my computer name",              "hostname"),
            ("show environment variables",            "set"),
            ("clear the screen",                      "cls"),
        ]),
        ("📂 Navigation", [
            ("go to the desktop",                     "cd %USERPROFILE%\\Desktop"),
            ("go to documents",                       "cd %USERPROFILE%\\Documents"),
            ("go back one folder",                    "cd .."),
            ("show current directory",                "cd"),
        ]),
    ]

    for category, examples in categories:
        t = Table(title=category, border_style="dim", show_header=True)
        t.add_column("You type",    style="white",      width=36)
        t.add_column("→ Command",   style="bold cyan",  width=44)
        for nl, cmd in examples:
            t.add_row(nl, cmd)
        console.print(t)
        console.print()


# ══════════════════════════════════════════════════════════════
def _show_safety_help():
    console.print()
    console.print(Panel(
        "[bold white]CmdBot checks every command through 3 safety levels\n"
        "before anything is executed.[/bold white]",
        border_style="yellow",
        title="[bold yellow]🛡️  Safety System[/bold yellow]"
    ))

    table = Table(border_style="yellow")
    table.add_column("Level",    style="bold cyan",   width=8)
    table.add_column("Type",     style="bold white",  width=16)
    table.add_column("Action",   style="bold",        width=22)
    table.add_column("Examples", style="dim",         width=38)

    table.add_row(
        "1", "🚫 Blocked",
        "[red]Never executes[/red]",
        "format, diskpart, bcdedit, reg delete"
    )
    table.add_row(
        "2", "⚠️  Dangerous",
        "[yellow]Needs YES confirm[/yellow]",
        "del, rmdir, shutdown, taskkill, netsh"
    )
    table.add_row(
        "3", "🧠 Suspicious",
        "[magenta]Always blocked[/magenta]",
        "powershell -enc, certutil -decode, wget"
    )
    table.add_row(
        "✅", "Safe",
        "[green]Runs immediately[/green]",
        "dir, echo, ipconfig, type, cd, hostname"
    )

    console.print(table)
    console.print(
        "\n[dim]The safety layer runs [bold]after[/bold] AI translation "
        "and [bold]before[/bold] execution — always.[/dim]\n"
    )