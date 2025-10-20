# Debate-bots

A refactored AI-powered debate simulator, built with a modular architecture, SOLID principles, and common design patterns.

## Features

-   **Modular Design:** Separated concerns for configuration, LLM interaction, display, and debate simulation.
-   **Extensible:** Easily add new LLM providers or display methods.
-   **Testable:** Components can be tested in isolation using dependency injection.
-   **GUI and Console Modes:** Run the debate with a graphical interface (PyQt5/Tkinter) or in the terminal.

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/asafbigel/Debate-bots.git
    cd Debate-bots
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv .venv
    ```

3.  **Activate the virtual environment:**

    *   **Windows (PowerShell):**

        ```bash
        .venv\Scripts\Activate.ps1
        ```

    *   **macOS/Linux (Bash/Zsh):**

        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**

    ```bash
    pip install -e .
    pip install -e .[dev] # For development dependencies like pytest
    ```

5.  **Configuration:**

    *   Create a `config.json` file in the project root with your desired LLM model:

        ```json
        {
            "model": "gpt-4o"
        }
        ```

    *   Create a `keys.json` file in the project root with your API keys. `litellm` will automatically pick these up from environment variables set by the `KeysLoader`:

        ```json
        {
            "OPENAI_API_KEY": "sk-...",
            "ANTHROPIC_API_KEY": "sk-...",
            "GEMINI_API_KEY": "AIza..."
        }
        ```

        *Note: `example_keys.json` is provided as a template for the structure of `keys.json`.*

## Usage

### Run with GUI (default)

```bash
python Political_bot.py
```

### Run in Console Mode

```bash
python examples/run_console.py
```

### Run Tests

```bash
pytest
```

## Project Structure

```
.venv/                # Python virtual environment
config.json           # LLM model configuration
keys.json             # API keys (ignored by .gitignore)
Political_bot.py      # Main entry point (GUI mode)
README.md             # Project documentation
pyproject.toml        # Project metadata and dependencies

debate/               # Core application package
├── __init__.py
├── app.py            # Application factory and runner
├── config.py         # Configuration and key loading
├── display.py        # Display strategies (GUI, Console)
├── llm_adapter.py    # LLM client adapter (for litellm)
└── simulator.py      # Debate simulation logic

examples/             # Example usage scripts
└── run_console.py    # Entry point for console mode

tests/                # Unit tests
└── test_simulator.py # Tests for the debate simulator