# Setting Up

Here's how to get the app running on your machine. It's pretty standard Python stuff!

## What you need

- **Python 3.10+**
- **uv** (It's a fast package manager we use)
- **Git**

## Quick Start

1. **Get the code:**

    ```bash
    git clone https://github.com/mighty-muffin/insecure-banking.git
    cd insecure-banking
    ```

2. **Install uv** (if you don't have it):

    ```bash
    # Mac/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Windows
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

3. **Set up the environment:**

    ```bash
    uv venv .venv --python 3.10
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

4. **Install dependencies:**

    ```bash
    uv sync --all-extras --dev --frozen
    ```

5. **Run it!**

    ```bash
    python src/manage.py migrate
    python src/manage.py runserver
    ```

That's it! Go to `http://127.0.0.1:8000` and start hacking.
