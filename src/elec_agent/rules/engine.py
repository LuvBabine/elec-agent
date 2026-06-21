# ⚡ elec-agent — NF C 15-100 Rule Engine
# Checks extracted components against French electrical code rules

import json
from pathlib import Path
from .voltage_drop import calc_voltage_drop, current_from_power

RULES_PATH = Path(__file__).parent / "nfc15100.json"


class RuleEngine:
    """
    NF C 15-100 compliance checker.

    Implements 4 critical rules from the French electrical standard:
        1. §523 — Breaker ↔ Cable section coordination
        2. §531 — Differential protection requirement
        3. §525 — Maximum voltage drop (3% lighting / 5% power)
        4. §771 — Maximum outlets per circuit (8 for 16A, 12 for 20A)
    """

    def __init__(self, rules_config: dict):
        """
        Initialize rule engine with configuration.

        Args:
            rules_config: Dict with keys:
                - standard: "NFC15100" (currently only supported)
                - strictness: "normal" | "strict"
        """
        # Load rules database from JSON
        with open(RULES_PATH, encoding="utf-8") as f:
            self.rules = json.load(f)

        self.strictness = rules_config.get("strictness", "normal")

    def check(self, components: list[dict]) -> list[dict]:
        """
        Run all rules on components and return issues.

        Args:
            components: List of component dictionaries

        Returns:
            List of issues with severity, message, and suggestion
        """
        issues = []
        for comp in components:
            issues += self._check_breaker_cable(comp)
            issues += self._check_differential(comp, components)
            issues += self._check_voltage_drop(comp)
            issues += self._check_socket_count(comp, components)
        return issues

    # ───────────────────────────────────────────────────────────────────────────
    # Rule 1: Breaker ↔ Cable Coordination (NF C 15-100 §523)
    # ───────────────────────────────────────────────────────────────────────────
    def _check_breaker_cable(self, comp: dict) -> list[dict]:
        """
        Check if cable section matches breaker rating.

        Rule: A 32A breaker requires minimum 4mm^2 cable.
        Too small = risk of overheating / fire.

        Args:
            comp: Component dictionary

        Returns:
            List of issues (empty if compliant)
        """
        issues = []

        # Only check circuit breakers
        if comp.get("type") != "circuit_breaker":
            return issues

        rating = comp.get("rating_A")
        section = comp.get("cable_section_mm2")

        # Skip if missing data
        if rating is None or section is None:
            return issues

        # Find minimum section for this breaker rating
        table = self.rules["breaker_cable_coordination"]["table"]
        min_section = None
        for row in sorted(table, key=lambda r: r["max_breaker_A"]):
            if rating <= row["max_breaker_A"]:
                min_section = row["min_section_mm2"]
                break

        # Flag error if cable is undersized
        if min_section and section < min_section:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": "NF C 15-100 §523",
                "severity": "error",
                "message": (
                    f"[{comp.get('id')}] {rating}A breaker: cable section {section}mm^2 too small "
                    f"(minimum {min_section}mm^2 required)"
                ),
                "suggestion": f"Replace cable with {min_section}mm^2 minimum, or reduce breaker rating.",
            })
        return issues

    # ───────────────────────────────────────────────────────────────────────────
    # Rule 2: Differential Protection (NF C 15-100 §531)
    # ───────────────────────────────────────────────────────────────────────────
    def _check_differential(self, comp: dict, all_comps: list[dict]) -> list[dict]:
        """
        Check if socket/lighting/motor circuits have differential protection.

        Rule: Every socket, lighting, and motor circuit must be protected
        by a 30mA differential switch (type AC).

        Args:
            comp: Component dictionary
            all_comps: Full component list (to check upstream protection)

        Returns:
            List of issues
        """
        issues = []
        protected_types = self.rules["differential_protection"]["mandatory_for"]

        # Skip if not a protected type
        if comp.get("type") not in protected_types:
            return issues

        # Check position
        position = comp.get("position")

        # Look for differential/RCB upstream in same position
        has_diff = any(
            c.get("type") in ("differential", "rcd") and c.get("position") == position
            for c in all_comps
        )

        if not has_diff:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": "NF C 15-100 §531",
                "severity": "error",
                "message": (
                    f"[{comp.get('id')}] {comp.get('type')} without differential protection "
                    f"(position: {position})"
                ),
                "suggestion": "Add 30mA differential switch (type AC) upstream of this circuit.",
            })
        return issues

    # ───────────────────────────────────────────────────────────────────────────
    # Rule 3: Voltage Drop (NF C 15-100 §525)
    # ───────────────────────────────────────────────────────────────────────────
    def _check_voltage_drop(self, comp: dict) -> list[dict]:
        """
        Check voltage drop along cable.

        Rule: Max 3% for lighting, 5% for power circuits.
        Too high = equipment may not work properly.

        Formula (single-phase): ΔU = (2 × ρ × L × I) / S

        Args:
            comp: Component dictionary

        Returns:
            List of issues
        """
        issues = []

        power = comp.get("load_power_W")
        length = comp.get("cable_length_m")
        section = comp.get("cable_section_mm2")
        comp_type = comp.get("type")

        # Skip if missing data
        if not all([power, length, section]):
            return issues

        # Calculate current from power
        current = current_from_power(power)

        # Calculate voltage drop
        result = calc_voltage_drop(current, length, section)

        # Check against threshold
        is_lighting = comp_type == "lighting"
        threshold = 3.0 if is_lighting else 5.0
        compliant = result["compliant_lighting"] if is_lighting else result["compliant_power"]

        if not compliant:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": "NF C 15-100 §525",
                "severity": "warning",
                "message": (
                    f"[{comp.get('id')}] Voltage drop {result['delta_U_percent']}% "
                    f"exceeds {threshold}% limit "
                    f"(cable {section}mm^2, {length}m, {power}W)"
                ),
                "suggestion": (
                    f"Increase cable section or reduce length. "
                    f"Current drop: {result['delta_U_V']}V."
                ),
            })
        return issues

    # ───────────────────────────────────────────────────────────────────────────
    # Rule 4: Max Outlets per Circuit (NF C 15-100 §771)
    # ───────────────────────────────────────────────────────────────────────────
    def _check_socket_count(self, comp: dict, all_comps: list[dict]) -> list[dict]:
        """
        Check number of outlets on a circuit.

        Rule: Max 8 outlets per 16A circuit, max 12 per 20A circuit.
        Too many = risk of overload.

        Args:
            comp: Component dictionary
            all_comps: Full component list

        Returns:
            List of issues
        """
        issues = []

        if comp.get("type") != "circuit_breaker":
            return issues

        rating = comp.get("rating_A")
        position = comp.get("position")

        # Count outlets on this circuit
        socket_count = sum(
            1 for c in all_comps
            if c.get("type") == "socket" and c.get("position") == position
        )

        if socket_count == 0:
            return issues

        rules = self.rules["socket_circuits"]

        # Check 16A circuit
        if rating == 16 and socket_count > rules["max_sockets_per_16A_circuit"]:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": "NF C 15-100 §771",
                "severity": "warning",
                "message": (
                    f"[{comp.get('id')}] 16A circuit with {socket_count} outlets "
                    f"(maximum {rules['max_sockets_per_16A_circuit']})"
                ),
                "suggestion": "Split into two separate 16A circuits.",
            })

        # Check 20A circuit
        elif rating == 20 and socket_count > rules["max_sockets_per_20A_circuit"]:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": "NF C 15-100 §771",
                "severity": "warning",
                "message": (
                    f"[{comp.get('id')}] 20A circuit with {socket_count} outlets "
                    f"(maximum {rules['max_sockets_per_20A_circuit']})"
                ),
                "suggestion": "Split into two separate 20A circuits.",
            })

        return issues
