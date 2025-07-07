# Azure OpenAI PR Review Agent

A simple, modular Python GitHub Action for automated pull request reviews using Azure OpenAI.

## Project Structure

```text
.
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── interfaces/          # Abstract interfaces (SOLID: Dependency Inversion)
│   │   ├── __init__.py
│   │   └── ai_provider.py
│   ├── models/              # Data models (SOLID: Single Responsibility)
│   │   ├── __init__.py
│   │   ├── pr_data.py
│   │   └── review_result.py
│   ├── providers/           # AI provider implementations
│   │   ├── __init__.py
│   │   └── azure_openai_provider.py
│   ├── services/            # Business logic (SOLID: Single Responsibility)
│   │   ├── __init__.py
│   │   └── pr_review_service.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── logger.py
├── requirements.txt
├── action.yml
└── .github/workflows/pr-review.yml
```

## Current Features

- ✅ Azure OpenAI integration for PR analysis
- ✅ Modular architecture following SOLID principles
- ✅ Extensible design for future AI providers

## Future Features (Documented for Extension)

- 🔄 Multiple AI providers (OpenAI, Anthropic, etc.)
- 🔄 Custom review templates
- 🔄 Code quality metrics
- 🔄 Security vulnerability detection
- 🔄 Performance analysis

## Setup

1. Set GitHub Secrets:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Design Principles Applied

- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Implementations are interchangeable
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions, not concretions

## Usage

The action automatically triggers on pull requests and posts review comments.
