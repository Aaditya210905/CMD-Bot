from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console
from src.executor import run_command
from src.safety import show_safety_levels

console = Console()

prompt_style = Style.from_dict({
    "prompt": "ansigreen bold",
})


def print_banner():
    console.print()
    console.print("[bold green]╔══════════════════════════════════════╗[/bold green]")
    console.print("[bold green]║      🤖  CmdBot  Activated!          ║[/bold green]")
    console.print("[bold green]║  Type Windows CMD commands directly  ║[/bold green]")
    console.print("[bold green]║  Type [bold yellow]exit[/bold yellow][bold green] to shut down            ║[/bold green]")
    console.print("[bold green]║  Type [bold cyan]help safety[/bold cyan][bold green] for safety info    ║[/bold green]")
    console.print("[bold green]╚══════════════════════════════════════╝[/bold green]")
    console.print()


def print_exit():
    console.print()
    console.print("[bold red]🛑  CmdBot shutting down... Goodbye![/bold red]")
    console.print()


def run_agent():
    print_banner()
    session = PromptSession()

    while True:
        try:
            user_input = session.prompt(
                [("class:prompt", "cmdbot > ")],
                style=prompt_style
            )

            user_input = user_input.strip()

            if not user_input:
                continue

            # 🚪 Exit
            if user_input.lower() in ["exit", "quit", "bye"]:
                print_exit()
                break

            # 📋 Help — safety table
            if user_input.lower() == "help safety":
                show_safety_levels()
                continue

            # ▶️ Execute
            run_command(user_input)

        except KeyboardInterrupt:
            console.print("\n[yellow]  Use 'exit' to quit CmdBot.[/yellow]")
            continue

        except EOFError:
            print_exit()
            break