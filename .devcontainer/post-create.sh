#!/bin/bash
set -e

echo "🚀 Setting up development environment..."

# Create virtual environment using uv
echo "📦 Creating virtual environment with uv..."
uv venv /workspaces/insecure-banking/.venv

# Install dependencies
echo "📥 Installing project dependencies..."
uv pip install -r requirements.txt

# Install development dependencies
echo "🛠️  Installing development dependencies..."
uv pip install -e ".[dev]"

# Install Playwright browsers for e2e testing
echo "🎭 Installing Playwright browsers..."
playwright install --with-deps chromium

# Set up pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Django settings
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DATABASE_URL=sqlite:///db.sqlite3
EOF
fi

# Initialize database
echo "🗄️  Initializing database..."
python manage.py migrate --noinput

# Create db.sqlite3 if it doesn't exist and run migrations
if [ ! -f db.sqlite3 ]; then
    echo "🔧 Creating database and loading initial data..."
    python manage.py migrate
fi

echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Quick start commands:"
echo "  - Run server: python manage.py runserver 0.0.0.0:8000"
echo "  - Run tests: pytest"
echo "  - Run e2e tests: pytest tests/e2e/"
echo "  - Format code: ruff format ."
echo "  - Lint code: ruff check ."
echo ""
