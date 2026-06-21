# ⚡ elec-agent

**Autonomous electrical schematic analyzer for international electrical standards.**

> An open-source AI agent that analyzes low-voltage electrical schematics against multiple standards: NF C 15-100 (France), IEC 60364 (Europe), NEC (USA), BS 7671 (UK).

---

## Supported Standards

| Standard | Country/Region | Status |
|---|---|---|
| **NF C 15-100** | France | ✅ Fully implemented |
| **IEC 60364** | Europe | ✅ Implemented |
| **NEC (NFPA 70)** | USA | ✅ Implemented |
| **BS 7671** | UK | ✅ Implemented |
| **CEC** | Canada | 📋 Planned |
| **VDE 0100** | Germany | 📋 Planned |

---

## Features

- 📷 **Image input** — drop a schematic photo or PDF scan
- 🔍 **LLM component extraction** — identifies breakers, cables, loads, protection devices
- 🌍 **Multi-standard compliance** — NF C 15-100, IEC 60364, NEC, BS 7671
- 📏 **Rule engine** — checks breaker ratings, cable sections, differential/GFCI protection
- 📉 **Voltage drop calculator** — flags cables where ΔU > 3% (lighting) or 5% (power)
- 📄 **PDF report output** — errors ranked by severity + correction suggestions + BOM

---

## Quickstart

```bash
git clone https://github.com/yourname/elec-agent
cd elec-agent
pip install -e .
elec-agent analyze examples/schema.png --output rapport.pdf
```

---

## Configuration

Edit `config.yaml`:

```yaml
llm:
  provider: ollama          # ollama | openai | anthropic
  model: qwen2.5vl          # vision model (qwen2.5vl, llava, gpt-4o)
  api_key: null

rules:
  standard: NFC15100        # Change to: IEC60364 | NEC2023 | BS7671
  strictness: normal

output:
  format: pdf
  language: fr
```

---

## Implemented Rules by Standard

### NF C 15-100 (France)

| Article | Rule |
|---|---|
| §523 | Breaker ↔ Cable section coordination |
| §531 | Differential 30mA protection requirement |
| §525 | Voltage drop max (3% lighting / 5% power) |
| §771 | Max outlets per circuit (8@16A, 12@20A) |

### IEC 60364 (Europe)

| Rule | Description |
|---|---|
| Cable coordination | IEC 60287 tables |
| Differential | 10mA bathrooms, 30mA general |
| Voltage drop | 3% lighting / 5% power (same) |
| Socket count | 10@16A, 14@20A |

### NEC (USA)

| Rule | Description |
|---|---|
| Cable sizing | NEC Table 310.16 (AWG gauge) |
| GFCI | 5mA sensitivity, mandatory in bathrooms/kitchen/outdoor |
| AFCI | Required in living rooms/bedrooms |
| Voltage drop | 3% branch / 5% feeder (recommended) |
| Outlet spacing | Max 6ft between outlets |

### BS 7671 (UK)

| Rule | Description |
|---|---|
| Cable sizing | BS 7671 Appendix 4 |
| RCD | 30mA mandatory for almost all circuits |
| Zs impedance | Earth loop impedance checks required |
| Socket count | Unlimited with valid load calculation |

---

## Contributing

Want to add more standards? See [CONTRIBUTING.md](CONTRIBUTING.md).

Pull requests welcome for:
- New electrical standards (CEC, VDE, etc.)
- Additional rules per standard
- Better LLM prompts for schematic extraction
- New parsers (SEE Electrical, EPLAN, etc.)

---

## License

MIT — free to use, modify, distribute.
