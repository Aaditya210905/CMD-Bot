from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from src.translator import translate
from src.executor import run_command
from src.safety import show_safety_levels

console = Console()

prompt_style = Style.from_dict({
    "prompt": "ansicyan bold",
})


def print_banner():
    console.print()
    console.print("[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║       🤖  CmdBot AI  Activated!          ║[/bold cyan]")
    console.print("[bold cyan]║  Speak plain English — I'll handle CMD   ║[/bold cyan]")
    console.print("[bold cyan]║  Type [bold yellow]exit[/bold yellow][bold cyan] to shut down               ║[/bold cyan]")
    console.print("[bold cyan]║  Type [bold green]help safety[/bold green][bold cyan] for safety rules       ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
    console.print()


def print_exit():
    console.print()
    console.print("[bold red]🛑  CmdBot shutting down... Goodbye![/bold red]")
    console.print()


def run_agent():
    print_banner()

    session = PromptSession()
    history = []          # 🧠 Keeps conversation context across turns

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

            # 📋 Help
            if user_input.lower() == "help safety":
                show_safety_levels()
                continue

            # 🧠 Step 1 — Translate English → CMD via LLM
            result = translate(user_input, history)

            if result.get("kind") == "clarification":
                question = result.get("question") or result.get("raw", "")

                # Keep clarification turns in context so the next user reply is grounded.
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": question})

                if len(history) > 20:
                    history = history[-20:]
                continue

            if not result["success"]:
                continue

            command = result["command"]

            # 🛡️ Step 2 — Run through safety + execute
            exec_result = run_command(command)

            # 💾 Step 3 — Save turn to history for context
            history.append({"role": "user",  "content": user_input})
            history.append({"role": "assistant",  "content": command})

            # 🔒 Keep history short — last 10 turns only (saves tokens)
            if len(history) > 20:
                history = history[-20:]

        except KeyboardInterrupt:
            console.print("\n[yellow]  Use 'exit' to quit CmdBot.[/yellow]")
            continue

        except EOFError:
            print_exit()
            break