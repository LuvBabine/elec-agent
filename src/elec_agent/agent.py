# ⚡ elec-agent — Main Agent Loop
# Pipeline: extract → check → report

import yaml
from pathlib import Path
from .parsers.image_parser import ImageParser
from .rules.engine import RuleEngine
from .reporters.pdf_report import PDFReporter


class ElecAgent:
    """
    Main agent class that orchestrates the analysis pipeline.

    Steps:
        1. Parse schematic (image/PDF/QET) → extract components
        2. Run NF C 15-100 rule engine on components
        3. Generate PDF compliance report
    """

    def __init__(self, config_path: Path = Path("config.yaml"), verbose: bool = False):
        """
        Initialize agent with configuration.

        Args:
            config_path: Path to YAML config file
            verbose: Enable detailed logging
        """
        # Load YAML configuration
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.verbose = verbose

        # Initialize pipeline components
        self.parser   = ImageParser(self.config["llm"])
        self.engine   = RuleEngine(self.config["rules"])
        self.reporter = PDFReporter(self.config["output"])

    def extract_components(self, schematic: Path) -> list[dict]:
        """
        Extract structured components from schematic using vision LLM.

        Args:
            schematic: Path to image, PDF, or .qet file

        Returns:
            List of component dictionaries with properties:
                - id: component identifier (e.g., "CB1")
                - type: component type (circuit_breaker, socket, lighting, etc.)
                - rating_A: breaker rating in amperes
                - cable_section_mm2: cable cross-section in mm^2
                - cable_length_m: cable length in meters
                - load_power_W: connected load power in watts
        """
        return self.parser.parse(schematic)

    def check_rules(self, components: list[dict]) -> list[dict]:
        """
        Run NF C 15-100 rule engine on extracted components.

        Args:
            components: List of component dictionaries

        Returns:
            List of issues, each with:
                - component_id: affected component
                - rule: NF C 15-100 article reference
                - severity: "error" or "warning"
                - message: human-readable description
                - suggestion: recommended correction
        """
        return self.engine.check(components)

    def generate_report(self, components: list[dict], issues: list[dict], output: Path):
        """
        Generate PDF compliance report.

        Args:
            components: Detected components list
            issues: List of compliance issues
            output: Path for output PDF file
        """
        self.reporter.generate(components, issues, output)
