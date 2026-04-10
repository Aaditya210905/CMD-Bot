# 🤖 CmdBot — Natural Language to Windows CMD

> Type plain English. CmdBot translates it into the right Windows
> command, checks it for safety, runs it, and shows you the output.

---

## ✨ Features

| Feature              | Description                                          |
|----------------------|------------------------------------------------------|
| 🧠 AI Translation    | Plain English → CMD via GPT-4o-mini                  |
| 🛡️ 3-Level Safety    | Blocks, warns, or confirms dangerous commands        |
| 📁 Context Tracking  | Knows your directory, last command, last output      |
| 🔗 Multi-Step Tasks  | Track complex operations across many commands        |
| 📋 Session Logging   | Every action saved to logs/ as .log and .json        |
| ⬆️ Arrow History     | ↑ ↓ arrows scroll through past commands              |
| 🔤 Tab Autocomplete  | Completes commands and natural language phrases      |
| 🐛 Debug Mode        | Set DEBUG=true in .env for verbose live output       |

---

## 🚀 Quick Start

### 1. Clone or download the project
```
git clone https://github.com/yourname/cmdbot.git
cd cmdbot
```

### 2. Create and activate virtual environment
```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Add your API key
Create a `.env` file in the project root:

If using OpenAI API key, it should look like this:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx    
DEBUG=false
```

### 5. a. For Cloud models (e.g. OpenAI, Hugging Face)
```
client = OpenAI(
  base_url="https://router.huggingface.co/v1",   # Hugging Face Inference API or change to your custom endpoint
  api_key="os.getenv('HF_API_KEY')"
)
```

### 5. b. For Local models (e.g. Ollama)
```
client = Ollama(
  base_url="http://localhost:11434",   # Ollama local server
  api_key="ollama"                  
)
```

### 6. Run CmdBot
```
python cmdbot.py
```

---

## 🌍 Run from Anywhere (Global Setup)

1. Create a scripts folder:
```
mkdir C:\cmdscripts
```

2. Create `C:\cmdscripts\cmdbot.bat`:
```bat
@echo off
set PROJECT_PATH=C:\Users\YourName\Desktop\cmdbot
call "%PROJECT_PATH%\venv\Scripts\activate.bat"
python "%PROJECT_PATH%\cmdbot.py"
call deactivate
```

3. Add `C:\cmdscripts` to your System PATH
4. Open any new terminal and type `cmdbot`

---

## 💬 Usage Examples

| You type                          | CMD command generated                        |
|-----------------------------------|----------------------------------------------|
| show all files                    | `dir`                                        |
| make a folder called myproject    | `mkdir myproject`                            |
| what is my ip address             | `ipconfig`                                   |
| show running processes            | `tasklist`                                   |
| go to the desktop                 | `cd %USERPROFILE%\Desktop`                   |
| how much disk space do i have     | `wmic logicaldisk get size,freespace,caption`|
| check if google is reachable      | `ping google.com`                            |
| clear the screen                  | `cls`                                        |

---

## ⌨️ Built-in Commands

| Command              | What it does                            |
|----------------------|-----------------------------------------|
| `exit`               | Shut down CmdBot                        |
| `help`               | Full help overview                      |
| `help examples`      | Show natural language examples          |
| `help safety`        | Explain the 3 safety levels             |
| `help commands`      | List all built-in commands              |
| `show logs`          | Session statistics table                |
| `show context`       | Current directory, state, history       |
| `start task: [name]` | Begin tracking a multi-step task        |
| `end task`           | End task and show completion summary    |
| `clear`              | Clear the terminal screen               |

---

## 🛡️ Safety Levels

| Level | Type         | Action              | Examples                      |
|-------|--------------|---------------------|-------------------------------|
| 1     | 🚫 Blocked   | Never executes      | format, diskpart, bcdedit     |
| 2     | ⚠️ Dangerous | Needs YES confirm   | del, rmdir, shutdown, taskkill|
| 3     | 🧠 Suspicious| Always blocked      | powershell -enc, certutil     |
| ✅    | Safe         | Runs immediately    | dir, echo, ipconfig, cd       |

---

## 📁 Project Structure

```
cmdbot/
├── logs/                    ← session logs (.log + .json)
├── src/
│   ├── agent.py             ← main loop orchestrator
│   ├── translator.py        ← English → CMD via OpenAI
│   ├── executor.py          ← runs commands safely
│   ├── safety.py            ← 3-level safety validation
│   ├── context.py           ← session state & cwd tracking
│   ├── completer.py         ← tab complete & arrow history
│   ├── help.py              ← help system
│   ├── logger.py            ← file + JSON logging
│   └── __init__.py
├── cmdbot.py                ← entry point
├── .env                     ← API key (never commit!)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔧 Configuration (`.env`)

```
OPENAI_API_KEY=sk-proj-xxxx     # Your OpenAI API key
DEBUG=false                      # Set true for verbose debug panels
```

---

## 📄 License
MIT — free to use, modify, and share.