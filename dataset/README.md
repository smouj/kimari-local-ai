# Kimari Dataset

This directory contains the dataset structure for training and fine-tuning Kimari models.

## Directory Structure

```
dataset/
├── raw/              # Raw, unprocessed data
├── cleaned/          # Cleaned and validated data
├── instructions/     # Instruction-response pairs
├── conversations/    # Multi-turn conversations
├── code/             # Code-specific examples
├── eval/             # Evaluation-only data (not for training)
└── README.md         # This file
```

## Data Format

Each entry should be a JSON file following this schema:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "Eres Kimari, asistente técnico local..."
    },
    {
      "role": "user",
      "content": "Tengo un error MODULE_NOT_FOUND en Node.js."
    },
    {
      "role": "assistant",
      "content": "Este error indica que Node.js no puede encontrar un módulo..."
    }
  ],
  "tags": ["nodejs", "debugging", "spanish", "server"],
  "quality_score": 4,
  "source": "real-world",
  "language": "es"
}
```

## Data Categories

- **Server errors** — Real debugging scenarios
- **Agent prompts** — Multi-step reasoning examples
- **Spanish technical** — Technical responses in Spanish
- **Code solutions** — Programming problems and solutions
- **Documentation** — Technical writing examples
- **Linux/Windows scripts** — Automation examples
- **Debugging patterns** — Troubleshooting methodologies

## Quality Guidelines

1. All code examples must be tested and correct
2. Technical responses must be accurate (no hallucination)
3. Spanish responses must use proper technical terminology
4. Destructive commands must be clearly marked
5. Security-sensitive operations must include warnings

## Contributing Data

To contribute training data:

1. Place raw data in `dataset/raw/`
2. Clean and validate following the format above
3. Move validated data to the appropriate subdirectory
4. Submit a pull request with a description of the data

## Important

**Do not include copyrighted material.** All data must be original or have compatible licensing.
