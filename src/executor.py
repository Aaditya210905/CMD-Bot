import subprocess
from rich.console import Console
from rich.panel import Panel
from src.safety import check_command, show_blocked_warning, show_dangerous_warning

console = Console()


def run_command(command: str) -> dict:
    """
    Run a command after passing it through the safety layer.
    """

    # 🛡️ Run through safety checks first
    safety = check_command(command)

    # 🚫 Level 1 & 3 — Hard blocked, never execute
    if not safety["allowed"]:
        show_blocked_warning(command, safety)
        return {"success": False, "output": "", "error": safety["reason"], "returncode": -1}

    # ⚠️ Level 2 — Dangerous, ask for YES
    if safety["level"] == "dangerous":
        confirmed = show_dangerous_warning(command, safety)
        if not confirmed:
            return {"success": False, "output": "", "error": "Cancelled by user.", "returncode": -1}

    # ▶️ Safe to run
    console.print(f"[dim]  ▶ :[/dim] [bold cyan]{command}[/bold cyan]\n")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )

        output  = result.stdout.strip()
        error   = result.stderr.strip()
        success = result.returncode == 0

        if output:
            console.print(Panel(
                f"[green]{output}[/green]",
                title="[bold green]✅ Output[/bold green]",
                border_style="green"
            ))

        if error:
            console.print(Panel(
                f"[red]{error}[/red]",
                title="[bold red]❌ Error[/bold red]",
                border_style="red"
            ))

        if not output and not error:
            console.print("[dim green]  ✅ Command executed successfully (no output).[/dim green]")

        console.print()
        return {"success": success, "output": output, "error": error, "returncode": result.returncode}

    except subprocess.TimeoutExpired:
        console.print(Panel("[red]⏱️  Timed out after 30 seconds.[/red]", border_style="red"))
        return {"success": False, "output": "", "error": "Timeout", "returncode": -1}

    except Exception as e:
        console.print(Panel(f"[red]Unexpected error: {e}[/red]", border_style="red"))
        return {"success": False, "output": "", "error": str(e), "returncode": -1}