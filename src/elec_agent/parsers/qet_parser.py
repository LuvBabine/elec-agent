# ⚡ elec-agent — QElectroTech Parser
# Reads .qet files (XML-based) directly without needing vision LLM

import xml.etree.ElementTree as ET
from pathlib import Path


# Map QElectroTech element names to our component types
ELEMENT_TYPE_MAP = {
    "disjoncteur": "circuit_breaker",
    "interrupteur differentiel": "differential",
    "fusible": "fuse",
    "contacteur": "contactor",
    "moteur": "motor",
    "prise": "socket",
    "eclairage": "lighting",
}


class QETParser:
    """
    QElectroTech file parser.

    QET stores schematics as XML — this parser extracts components directly
    without needing a vision LLM (faster, more accurate for digital files).
    """

    def parse(self, path: Path) -> list[dict]:
        """
        Parse .qet file and extract components.

        Args:
            path: Path to QElectroTech .qet file

        Returns:
            List of component dictionaries
        """
        tree = ET.parse(path)
        root = tree.getroot()
        components = []

        for elem in root.iter("element"):
            name = elem.get("name", "").lower()

            # Determine component type
            comp_type = "other"
            for key, val in ELEMENT_TYPE_MAP.items():
                if key in name:
                    comp_type = val
                    break

            # Extract properties from element metadata
            properties = {
                prop.get("name"): prop.get("value")
                for prop in elem.iter("elementinformation")
            }

            components.append({
                "id": elem.get("uuid", f"elem_{len(components)}"),
                "type": comp_type,
                "raw_name": elem.get("name"),
                "rating_A": self._safe_float(properties.get("calibre")),
                "poles": self._safe_int(properties.get("poles")),
                "cable_section_mm2": self._safe_float(properties.get("section")),
                "cable_length_m": self._safe_float(properties.get("longueur")),
                "load_power_W": self._safe_float(properties.get("puissance")),
            })

        return components

    def _safe_float(self, val):
        """Convert to float, return None if invalid."""
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    def _safe_int(self, val):
        """Convert to int, return None if invalid."""
        try:
            return int(val)
        except (TypeError, ValueError):
            return None
