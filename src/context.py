import os
import re
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class SessionContext:
    """
    Tracks everything about the current CmdBot session:
    - Current working directory (updates after every cd command)
    - Command history with results
    - Session variables set by user
    - Multi-step task tracking
    """

    def __init__(self):
        self.cwd            = os.getcwd()           # Current working directory
        self.session_start  = datetime.now()
        self.command_history= []                    # List of past commands + results
        self.variables      = {}                    # User-defined session variables
        self.dir_stack      = []                    # pushd/popd directory stack
        self.last_command   = ""
        self.last_output    = ""
        self.last_success   = None
        self.step_task      = None                  # Active multi-step task name
        self.step_history   = []                    # Steps completed so far


    # ══════════════════════════════════════════════
    # 📁 DIRECTORY TRACKING
    # ══════════════════════════════════════════════

    def _normalize_path(self, raw_path: str) -> str:
        """Expand vars and resolve relative paths against current session cwd."""
        target = raw_path.strip().strip('"')
        target = os.path.expandvars(target)

        if not target:
            return ""

        if os.path.isabs(target):
            return os.path.normpath(target)

        return os.path.normpath(os.path.join(self.cwd, target))


    def update_cwd(self, command: str, success: bool):
        """
        Keep session cwd in sync for directory-changing commands.
        Handles: cd, chdir, pushd, popd.
        """
        if not success:
            return

        raw_cmd = command.strip()
        if not raw_cmd:
            return

        cmd_lower = raw_cmd.lower()

        # popd has no argument, so handle first.
        if cmd_lower == "popd":
            if self.dir_stack:
                old_cwd = self.cwd
                self.cwd = self.dir_stack.pop()
                if old_cwd != self.cwd:
                    console.print(f"[dim]  📁 Directory changed → [cyan]{self.cwd}[/cyan][/dim]\n")
            return

        # Match cd/chdir/pushd with or without a space after command.
        match = re.match(r"^(cd|chdir|pushd)(.*)$", raw_cmd, flags=re.IGNORECASE)
        if not match:
            return

        op = match.group(1).lower()
        args = match.group(2).strip()

        # "cd" alone only prints current directory in cmd.
        if op in {"cd", "chdir"} and not args:
            return

        # Support "cd /d <path>" style.
        if op in {"cd", "chdir"}:
            args = re.sub(r"^/d\s*", "", args, flags=re.IGNORECASE).strip()

        target = self._normalize_path(args)
        if not target or not os.path.isdir(target):
            return

        if op == "pushd":
            self.dir_stack.append(self.cwd)

        old_cwd = self.cwd
        self.cwd = target
        if old_cwd != self.cwd:
            console.print(f"[dim]  📁 Directory changed → [cyan]{self.cwd}[/cyan][/dim]\n")


    def get_cwd_display(self) -> str:
        """Return a short display version of cwd."""
        home = os.path.expanduser("~")
        if self.cwd.startswith(home):
            return "~" + self.cwd[len(home):]
        return self.cwd


    # ══════════════════════════════════════════════
    # 💾 COMMAND HISTORY
    # ══════════════════════════════════════════════

    def record_command(self, user_input: str, command: str,
                       success: bool, output: str, error: str):
        """Save a completed command to history."""
        self.last_command = command
        self.last_output  = output[:300] if output else ""
        self.last_success = success

        entry = {
            "timestamp"  : datetime.now().strftime("%H:%M:%S"),
            "user_input" : user_input,
            "command"    : command,
            "success"    : success,
            "output"     : output[:300] if output else "",
            "error"      : error[:200] if error else "",
            "cwd"        : self.cwd,
        }
        self.command_history.append(entry)

        # Keep last 30 entries only
        if len(self.command_history) > 30:
            self.command_history = self.command_history[-30:]

        # Track multi-step progress
        if self.step_task:
            self.step_history.append({
                "step"    : len(self.step_history) + 1,
                "command" : command,
                "success" : success
            })


    # ══════════════════════════════════════════════
    # 🔗 MULTI-STEP TASK TRACKING
    # ══════════════════════════════════════════════

    def start_task(self, task_name: str):
        """Begin tracking a named multi-step task."""
        self.step_task    = task_name
        self.step_history = []
        console.print(f"[dim cyan]  🔗 Task started: [bold]{task_name}[/bold][/dim cyan]\n")


    def end_task(self):
        """Mark the current multi-step task as complete."""
        if self.step_task:
            total   = len(self.step_history)
            success = sum(1 for s in self.step_history if s["success"])
            console.print(
                f"[dim cyan]  ✅ Task [bold]{self.step_task}[/bold] complete — "
                f"{success}/{total} steps succeeded.[/dim cyan]\n"
            )
        self.step_task    = None
        self.step_history = []


    # ══════════════════════════════════════════════
    # 🧠 BUILD CONTEXT STRING FOR AI PROMPT
    # ══════════════════════════════════════════════

    def build_context_block(self) -> str:
        """
        Build a context summary injected into every AI prompt.
        This tells GPT exactly where the user is and what just happened.
        """
        lines = [
            f"CURRENT DIRECTORY : {self.cwd}",
            f"SESSION STARTED   : {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}",
            f"COMMANDS RUN      : {len(self.command_history)}",
        ]

        if self.last_command:
            lines.append(f"LAST COMMAND      : {self.last_command}")
            lines.append(f"LAST SUCCESS      : {self.last_success}")
            if self.last_output:
                # Only feed a short snippet of last output to save tokens
                snippet = self.last_output[:200].replace("\n", " | ")
                lines.append(f"LAST OUTPUT       : {snippet}")

        if self.step_task:
            lines.append(f"ACTIVE TASK       : {self.step_task}")
            lines.append(f"STEPS DONE        : {len(self.step_history)}")

        if self.variables:
            vars_str = ", ".join(f"{k}={v}" for k, v in self.variables.items())
            lines.append(f"SESSION VARIABLES : {vars_str}")

        # Recent command summary (last 3)
        if len(self.command_history) >= 2:
            recent = self.command_history[-3:]
            recent_str = " → ".join(e["command"] for e in recent)
            lines.append(f"RECENT COMMANDS   : {recent_str}")

        return "\n".join(lines)


    # ══════════════════════════════════════════════
    # 📊 DISPLAY CONTEXT TABLE
    # ══════════════════════════════════════════════

    def show_context(self):
        """Print a rich table of current session context."""

        table = Table(title="🧠 Session Context", border_style="cyan")
        table.add_column("Property",  style="bold white", width=22)
        table.add_column("Value",     style="cyan")

        table.add_row("Current Directory",  self.cwd)
        table.add_row("Session Started",    self.session_start.strftime("%Y-%m-%d %H:%M:%S"))
        table.add_row("Commands Run",       str(len(self.command_history)))
        table.add_row("Last Command",       self.last_command or "—")
        table.add_row("Last Status",
            "[green]✅ Success[/green]" if self.last_success is True
            else "[red]❌ Failed[/red]" if self.last_success is False
            else "—"
        )
        table.add_row("Active Task",        self.step_task or "—")

        if self.variables:
            for k, v in self.variables.items():
                table.add_row(f"  var:{k}", v)

        console.print()
        console.print(table)

        # Recent history
        if self.command_history:
            hist = Table(title="🕘 Command History", border_style="dim")
            hist.add_column("#",        style="dim",   width=4)
            hist.add_column("Time",     style="dim",   width=10)
            hist.add_column("Input",    style="white", width=24)
            hist.add_column("Command",  style="cyan",  width=24)
            hist.add_column("Result",   style="bold",  width=8)

            for i, e in enumerate(self.command_history[-8:], 1):
                result = "[green]✅[/green]" if e["success"] else "[red]❌[/red]"
                hist.add_row(
                    str(i),
                    e["timestamp"],
                    e["user_input"][:22],
                    e["command"][:22],
                    result
                )
            console.print(hist)

        console.print()