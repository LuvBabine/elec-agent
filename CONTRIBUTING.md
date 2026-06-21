# Contributing to elec-agent

Thanks for your interest! Here's how to help:

## Ways to contribute

- 🐛 **Bug reports** — open an issue with your schematic (anonymized) and the wrong output
- 📏 **Extend the rules database** — add rules to `nfc15100.json` with their article reference
- 🌍 **New standards** — implement `IEC60364.json` for international support
- 🔌 **New parsers** — add support for SEE Electrical, EPLAN, Autocad Electrical exports
- 🧪 **Tests** — add test cases in `tests/`

## Development setup

```bash
git clone https://github.com/yourname/elec-agent
cd elec-agent
pip install -e ".[dev]"
pytest tests/
```

## Pull request guidelines

1. One feature or fix per PR
2. Add a test for every new rule
3. Cite the NF C 15-100 article number in rule descriptions
4. Run `pytest` before submitting — all tests must pass

## Code style

- Python 3.10+
- Type hints everywhere
- Docstrings for all public functions
