# ⚡ elec-agent — Multi-Norm Rule Engine
# Supports NF C 15-100, NEC, IEC 60364, BS 7671, etc.

import json
from pathlib import Path
from .voltage_drop import calc_voltage_drop, current_from_power
from .norms import get_norm, NORMS

RULES_PATH = Path(__file__).parent / "norms"


class RuleEngine:
    """
    Multi-norm compliance checker.

    Supports:
        - NF C 15-100 (France)
        - IEC 60364 (Europe)
        - NEC NFPA 70 (USA)
        - BS 7671 (UK)

    Initialize with:
        engine = RuleEngine({"standard": "NFC15100", "strictness": "normal"})
    """

    def __init__(self, rules_config: dict):
        """
        Initialize rule engine with configuration.

        Args:
            rules_config: Dict with keys:
                - standard: "NFC15100" | "IEC60364" | "NEC2023" | "BS7671"
                - strictness: "normal" | "strict"
        """
        # Load rules for selected standard
        self.standard = rules_config.get("standard", "NFC15100")
        self.rules = get_norm(self.standard)

        if self.rules is None:
            raise ValueError(f"Unknown standard: {self.standard}. Use: {list(NORMS.keys())}")

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

    def _check_breaker_cable(self, comp: dict) -> list[dict]:
        """Check breaker-cable coordination per selected standard."""
        issues = []

        if comp.get("type") != "circuit_breaker":
            return issues

        rating = comp.get("rating_A")
        section = comp.get("cable_section_mm2")

        if rating is None or section is None:
            return issues

        table = self.rules["breaker_cable_coordination"]["table"]
        min_section = None

        for row in sorted(table, key=lambda r: r["max_breaker_A"]):
            if rating <= row["max_breaker_A"]:
                min_section = row["min_section_mm2"]
                break

        if min_section and section < min_section:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": f"{self.standard} - Cable coordination",
                "severity": "error",
                "message": (
                    f"[{comp.get('id')}] {rating}A breaker: cable section {section}mm^2 too small "
                    f"(minimum {min_section}mm^2 required per {self.standard})"
                ),
                "suggestion": f"Replace cable with {min_section}mm^2 minimum, or reduce breaker rating.",
            })
        return issues

    def _check_differential(self, comp: dict, all_comps: list[dict]) -> list[dict]:
        """Check differential/RCD/GFCI protection per selected standard."""
        issues = []

        if self.standard == "NEC2023":
            # NEC uses GFCI/AFCI instead of differential
            rules = self.rules.get("gfci_protection", {})
            protection_type = "GFCI"
        else:
            rules = self.rules.get("differential_protection", {})
            protection_type = "differential" if self.standard != "BS7671" else "RCD"

        protected_types = rules.get("mandatory_for", [])

        if comp.get("type") not in protected_types:
            return issues

        position = comp.get("position")

        if self.standard == "NEC2023":
            has_protection = any(
                c.get("type") in ("gfci", "afc") and c.get("position") == position
                for c in all_comps
            )
        else:
            has_protection = any(
                c.get("type") in ("differential", "rcd") and c.get("position") == position
                for c in all_comps
            )

        if not has_protection:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": f"{self.standard} - {protection_type} protection",
                "severity": "error",
                "message": (
                    f"[{comp.get('id')}] {comp.get('type')} without {protection_type} protection "
                    f"(position: {position})"
                ),
                "suggestion": f"Add {protection_type} protection upstream of this circuit.",
            })
        return issues

    def _check_voltage_drop(self, comp: dict) -> list[dict]:
        """Check voltage drop per selected standard."""
        issues = []

        power = comp.get("load_power_W")
        length = comp.get("cable_length_m")
        section = comp.get("cable_section_mm2")
        comp_type = comp.get("type")

        if not all([power, length, section]):
            return issues

        current = current_from_power(power)
        result = calc_voltage_drop(current, length, section)

        is_lighting = comp_type == "lighting"
        threshold = 3.0 if is_lighting else 5.0
        compliant = result["compliant_lighting"] if is_lighting else result["compliant_power"]

        if not compliant:
            issues.append({
                "component_id": comp.get("id", "?"),
                "rule": f"{self.standard} - Voltage drop",
                "severity": "warning",
                "message": (
                    f"[{comp.get('id')}] Voltage drop {result['delta_U_percent']}% "
                    f"exceeds {threshold}% limit "
                    f"(cable {section}mm^2, {length}m, {power}W)"
                ),
                "suggestion": f"Increase cable section or reduce length. Current drop: {result['delta_U_V']}V.",
            })
        return issues

    def _check_socket_count(self, comp: dict, all_comps: list[dict]) -> list[dict]:
        """Check socket count per circuit per selected standard."""
        issues = []

        if comp.get("type") != "circuit_breaker":
            return issues

        rating = comp.get("rating_A")
        position = comp.get("position")

        socket_count = sum(
            1 for c in all_comps
            if c.get("type") == "socket" and c.get("position") == position
        )

        if socket_count == 0:
            return issues

        rules = self.rules.get("socket_circuits", {})

        if self.standard == "NEC2023":
            # NEC doesn't limit socket count, uses load calculation
            return issues
        elif self.standard == "BS7671":
            # UK allows unlimited sockets with valid load calculation
            return issues
        else:
            # NF C 15-100 / IEC 60364
            max_16A = rules.get("max_sockets_per_16A_circuit", 8)
            max_20A = rules.get("max_sockets_per_20A_circuit", 12)

            if rating == 16 and socket_count > max_16A:
                issues.append({
                    "component_id": comp.get("id", "?"),
                    "rule": f"{self.standard} - Socket count",
                    "severity": "warning",
                    "message": f"[{comp.get('id')}] {rating}A circuit with {socket_count} sockets (maximum {max_16A})",
                    "suggestion": "Split into two separate circuits.",
                })
            elif rating == 20 and socket_count > max_20A:
                issues.append({
                    "component_id": comp.get("id", "?"),
                    "rule": f"{self.standard} - Socket count",
                    "severity": "warning",
                    "message": f"[{comp.get('id')}] {rating}A circuit with {socket_count} sockets (maximum {max_20A})",
                    "suggestion": "Split into two separate circuits.",
                })

        return issues
