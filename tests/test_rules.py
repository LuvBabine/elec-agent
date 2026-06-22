"""
Unit tests for elec-agent rule engine and voltage drop calculator.
Run with: pytest tests/
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from elec_agent.rules.voltage_drop import calc_voltage_drop, current_from_power
from elec_agent.rules.engine import RuleEngine


@pytest.fixture
def engine():
    # BUG FIX: "standard" key was missing → caused get_norm(None) → returned None → crash
    return RuleEngine({"standard": "NFC15100", "strictness": "normal"})


# ── Voltage drop tests ─────────────────────────────────────────────────────────

def test_voltage_drop_compliant():
    """16A, 10m, 2.5mm² → should be compliant for power circuits."""
    I = current_from_power(3000)
    result = calc_voltage_drop(I, 10, 2.5)
    assert result["compliant_power"] is True


def test_voltage_drop_too_long():
    """6A, 80m, 1.5mm² → should exceed 3% for lighting."""
    I = current_from_power(1200)
    result = calc_voltage_drop(I, 80, 1.5)
    assert result["compliant_lighting"] is False


def test_voltage_drop_three_phase():
    """Three-phase calculation should give lower drop than single-phase."""
    I = 20.0
    r1 = calc_voltage_drop(I, 50, 6.0, phases=1)
    r3 = calc_voltage_drop(I, 50, 6.0, phases=3)
    assert r3["delta_U_V"] < r1["delta_U_V"]


# ── Rule engine tests ──────────────────────────────────────────────────────────

def test_breaker_cable_ok(engine):
    """16A breaker with 2.5mm² cable → no issue."""
    comp = {"id": "CB1", "type": "circuit_breaker", "rating_A": 16,
            "cable_section_mm2": 2.5, "position": "tgbt"}
    issues = engine._check_breaker_cable(comp)
    assert len(issues) == 0


def test_breaker_cable_undersized(engine):
    """32A breaker with 2.5mm² cable → should flag error (min 4mm²)."""
    comp = {"id": "CB2", "type": "circuit_breaker", "rating_A": 32,
            "cable_section_mm2": 2.5, "position": "tgbt"}
    issues = engine._check_breaker_cable(comp)
    assert len(issues) == 1
    assert issues[0]["severity"] == "error"
    # BUG FIX: rule string is "NFC15100 §523 - Cable coordination", not just "§523"
    assert "§523" in issues[0]["rule"]


def test_missing_differential(engine):
    """Socket without differential in same position → should flag error."""
    components = [
        {"id": "S1", "type": "socket", "position": "bureau"},
    ]
    issues = engine._check_differential(components[0], components)
    assert len(issues) == 1
    assert issues[0]["severity"] == "error"


def test_differential_present(engine):
    """Socket with RCD in same position → no issue."""
    components = [
        {"id": "RCD1", "type": "rcd",    "position": "bureau"},
        {"id": "S1",   "type": "socket", "position": "bureau"},
    ]
    issues = engine._check_differential(components[1], components)
    assert len(issues) == 0


def test_too_many_sockets(engine):
    """16A circuit with 10 sockets → should flag warning (max 8)."""
    components = [{"id": f"S{i}", "type": "socket", "position": "salon"} for i in range(10)]
    cb = {"id": "CB1", "type": "circuit_breaker", "rating_A": 16, "position": "salon"}
    components.append(cb)
    issues = engine._check_socket_count(cb, components)
    assert len(issues) == 1
    assert issues[0]["severity"] == "warning"
