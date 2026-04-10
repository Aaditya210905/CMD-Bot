from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from src.translator import translate
from src.executor import run_command
from src.safety import show_safety_levels
from src.logger import log_input, log_session_start,log_session_end, show_session_summary
from src.context import SessionContext

console = Console()

prompt_style = Style.from_dict({
    "prompt": "ansicyan bold",
})


def print_banner():
    console.print()
    console.print("[bold cyan]╔══════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║       🤖  CmdBot AI  Activated!          ║[/bold cyan]")
    console.print("[bold cyan]║  Speak plain English — I'll handle CMD   ║[/bold cyan]")
    console.print("[bold cyan]║  Type [bold yellow]exit[/bold yellow][bold cyan] to shut down                  ║[/bold cyan]")
    console.print("[bold cyan]║  Type [bold green]help safety[/bold green][bold cyan] for safety rules       ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════════╝[/bold cyan]")
    console.print()


def print_exit():
    console.print()
    console.print("[bold red]🛑  CmdBot shutting down... Goodbye![/bold red]")
    console.print()


def run_agent():
    print_banner()
    log_session_start()                     # ✅ Log session start

    session = PromptSession()
    ctx = SessionContext()
    history = []          # 🧠 Keeps conversation context across turns
    command_count = 0     # ✅ Track total commands executed

    while True:
        try:
            cwd_short = ctx.get_cwd_display()
            user_input = session.prompt(
                [
                    ("class:prompt", "cmdbot "),
                    ("class:path",   f"[{cwd_short}]"),
                    ("class:prompt", " > "),
                ],
                style=Style.from_dict({
                    "prompt" : "ansicyan bold",
                    "path"   : "ansiyellow",
                })
            )

            user_input = user_input.strip()

            if not user_input:
                continue

            # 🚪 Exit
            if user_input.lower() in ["exit", "quit", "bye"]:
                log_session_end(command_count)  # ✅ Log session end with total commands
                print_exit()
                break

            # 📋 Help
            if user_input.lower() == "help safety":
                show_safety_levels()
                continue

            # 📊 Show logs summary
            if user_input.lower() == "show logs":
                show_session_summary()
                continue

            if user_input.lower() == "show context":
                ctx.show_context()
                continue

            # ── Detect multi-step task markers ─────────────────
            lower = user_input.lower()
            if lower.startswith("start task:"):
                task_name = user_input[11:].strip()
                ctx.start_task(task_name)
                continue

            if lower in ["end task", "finish task", "done task"]:
                ctx.end_task()
                continue

            log_input(user_input)               # ✅ Log user input

            # — Translate English → CMD via LLM
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
            command_count += 1

            # — Run through safety + execute
            exec_result = run_command(command, cwd=ctx.cwd)
            # ── 📁 Update working directory ────────────────────
            ctx.update_cwd(command, exec_result["success"])

            # ─ Record to context history ───────────────────
            ctx.record_command(
                user_input = user_input,
                command    = command,
                success    = exec_result["success"],
                output     = exec_result.get("output", ""),
                error      = exec_result.get("error", "")
            )

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
            log_session_end(command_count)
            print_exit()
            break