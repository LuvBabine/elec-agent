# ⚡ elec-agent

**Autonomous electrical schematic analyzer for NF C 15-100 compliance.**

> An open-source AI agent that analyzes low-voltage electrical schematics (industrial/residential) against French NF C 15-100 standard rules — something no existing tool does.

---

## Why elec-agent?

Existing LLM+schematic tools (KiCad-happy, Circuitry.ai, Netlist.io) all target **PCB/electronics** schematics.
Nobody covers **industrial/residential wiring schematics**: distribution boards, armoires électriques, câblage BT — the world of BTS Électrotechnique.

`elec-agent` fills that gap.

---

## Features

- 📷 **Image input** — drop a schematic photo or PDF scan
- 🔍 **LLM component extraction** — identifies breakers, cables, loads, protection devices
- 📏 **NF C 15-100 rule engine** — checks breaker ratings, cable sections, differential protection
- 📉 **Voltage drop calculator** — flags cables where ΔU > 3% (lighting) or 5% (power)
- 📄 **PDF report output** — errors ranked by severity + correction suggestions + BOM

---

## Quickstart

```bash
git clone https://github.com/yourname/elec-agent
cd elec-agent
pip install -e .
elec-agent analyze examples/schema_exemple.png --output rapport.pdf
```

---

## Configuration

Edit `config.yaml`:

```yaml
llm:
  provider: ollama          # ollama | openai | anthropic
  model: llama3.2-vision    # any vision-capable model
  api_key: null             # set for openai/anthropic

rules:
  standard: NFC15100        # currently only NFC15100
  strictness: normal        # normal | strict

output:
  format: pdf               # pdf | txt | json
  language: fr              # fr | en
```

---

## Architecture

```
elec-agent/
├── src/elec_agent/
│   ├── agent.py            # Main agent loop
│   ├── parsers/
│   │   ├── image_parser.py # Vision LLM → structured component list
│   │   └── qet_parser.py   # QElectroTech .qet file parser
│   ├── rules/
│   │   ├── engine.py       # Rule checker
│   │   ├── nfc15100.json   # NF C 15-100 rules database
│   │   └── voltage_drop.py # Voltage drop calculator
│   └── reporters/
│       └── pdf_report.py   # PDF report generator
├── config.yaml
├── pyproject.toml
└── tests/
```

---

## Supported inputs

| Format | Status |
|---|---|
| Image (PNG, JPG) | ✅ Supported |
| PDF scan | ✅ Supported |
| QElectroTech (.qet) | 🚧 In progress |
| SEE Electrical export | 📋 Planned |

---

## Implemented Rules (NF C 15-100)

| Article | Rule | Severity |
|---|---|---|
| §523 | Breaker ↔ Cable section coordination | Error |
| §531 | Differential protection requirement | Error |
| §525 | Voltage drop max (3% lighting / 5% power) | Warning |
| §771 | Max outlets per circuit (8@16A, 12@20A) | Warning |

---

## Contributing

Pull requests welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — free to use, modify, distribute.
