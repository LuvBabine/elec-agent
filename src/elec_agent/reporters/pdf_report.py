# ⚡ elec-agent — PDF Report Generator
# Creates professional compliance reports using ReportLab

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


# Color palette
RED    = colors.HexColor("#E53935")
ORANGE = colors.HexColor("#FB8C00")
GREEN  = colors.HexColor("#43A047")
DARK   = colors.HexColor("#212121")
LIGHT  = colors.HexColor("#F5F5F5")
BLUE   = colors.HexColor("#1565C0")


class PDFReporter:
    """
    Professional PDF report generator.

    Output includes:
        - Header with project info
        - Summary table (components, errors, warnings)
        - Detailed issues table with corrections
        - Bill of Materials (BOM)
        - Disclaimer footer
    """

    def __init__(self, output_config: dict):
        """
        Initialize reporter with output configuration.

        Args:
            output_config: Dict with keys:
                - format: "pdf"
                - language: "fr" | "en"
        """
        self.language = output_config.get("language", "fr")

    def generate(self, components: list[dict], issues: list[dict], output: Path):
        """
        Generate PDF compliance report.

        Args:
            components: Detected components list
            issues: List of compliance issues
            output: Path for output PDF file
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output),
            pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )
        styles = getSampleStyleSheet()
        story  = []  # PDF content list

        # ───────────────────────────────────────────────────────────────────────
        # Header
        # ───────────────────────────────────────────────────────────────────────
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"],
            fontSize=22, textColor=BLUE, spaceAfter=4,
        )
        story.append(Paragraph("⚡ elec-agent — NF C 15-100 Compliance Report", title_style))
        story.append(Paragraph(
            f"Generated on {datetime.now().strftime('%d/%m/%Y at %H:%M')}",
            styles["Normal"]
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=BLUE, spaceAfter=12))

        # ───────────────────────────────────────────────────────────────────────
        # Summary Table
        # ───────────────────────────────────────────────────────────────────────
        errors   = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]

        summary_data = [
            ["Components Detected", "Errors (Non-compliance)", "Warnings"],
            [str(len(components)), str(len(errors)), str(len(warnings))],
        ]
        summary_table = Table(summary_data, colWidths=[5.5*cm, 6*cm, 5.5*cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (1, 1), (1, 1), RED if errors else GREEN),
            ("BACKGROUND", (2, 1), (2, 1), ORANGE if warnings else GREEN),
            ("TEXTCOLOR",  (0, 1), (-1, 1), colors.white),
            ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
            ("FONTSIZE",   (0, 0), (-1, 0), 11),
            ("FONTSIZE",   (0, 1), (-1, 1), 20),
            ("FONTNAME",   (0, 1), (-1, 1), "Helvetica-Bold"),
            ("BOX",        (0, 0), (-1, -1), 1, colors.white),
            ("INNERGRID",  (0, 0), (-1, -1), 0.5, colors.white),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 16))

        # ───────────────────────────────────────────────────────────────────────
        # Issues Table
        # ───────────────────────────────────────────────────────────────────────
        h2 = ParagraphStyle("H2", parent=styles["Heading2"],
                             textColor=DARK, spaceBefore=12, spaceAfter=6)

        story.append(Paragraph("Detected Non-compliance Issues", h2))

        if not issues:
            story.append(Paragraph(
                "✅ No non-compliance issues detected. Schematic complies with NF C 15-100.",
                styles["Normal"]
            ))
        else:
            issue_data = [["Severity", "Component", "Rule", "Message", "Correction"]]
            for issue in sorted(issues, key=lambda x: 0 if x["severity"]=="error" else 1):
                sev_color = RED if issue["severity"] == "error" else ORANGE
                issue_data.append([
                    issue["severity"].upper(),
                    issue.get("component_id", "?"),
                    issue.get("rule", ""),
                    Paragraph(issue["message"], styles["Normal"]),
                    Paragraph(issue.get("suggestion", ""), styles["Normal"]),
                ])

            col_widths = [2*cm, 2.5*cm, 3*cm, 5.5*cm, 4*cm]
            issue_table = Table(issue_data, colWidths=col_widths, repeatRows=1)
            style = [
                ("BACKGROUND",   (0, 0), (-1, 0), DARK),
                ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
                ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",     (0, 0), (-1, -1), 8),
                ("ALIGN",        (0, 0), (2, -1), "CENTER"),
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT, colors.white]),
                ("BOX",          (0, 0), (-1, -1), 0.5, colors.grey),
                ("INNERGRID",    (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ]
            for i, issue in enumerate(issues, start=1):
                c = RED if issue["severity"] == "error" else ORANGE
                style.append(("TEXTCOLOR", (0, i), (0, i), c))
                style.append(("FONTNAME",  (0, i), (0, i), "Helvetica-Bold"))
            issue_table.setStyle(TableStyle(style))
            story.append(issue_table)

        story.append(Spacer(1, 16))

        # ───────────────────────────────────────────────────────────────────────
        # Bill of Materials (BOM)
        # ───────────────────────────────────────────────────────────────────────
        story.append(Paragraph("Bill of Materials (BOM)", h2))

        bom_data = [["ID", "Type", "Rating (A)", "Section (mm^2)", "Length (m)", "Power (W)"]]
        for c in components:
            bom_data.append([
                c.get("id", ""),
                c.get("type", ""),
                str(c.get("rating_A", "")),
                str(c.get("cable_section_mm2", "")),
                str(c.get("cable_length_m", "")),
                str(c.get("load_power_W", "")),
            ])

        bom_table = Table(bom_data, colWidths=[2*cm, 3.5*cm, 2.5*cm, 3*cm, 2.5*cm, 3.5*cm],
                          repeatRows=1)
        bom_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
            ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [LIGHT, colors.white]),
            ("BOX",           (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID",     (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ]))
        story.append(bom_table)

        # ───────────────────────────────────────────────────────────────────────
        # Footer (disclaimer)
        # ───────────────────────────────────────────────────────────────────────
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        footer_style = ParagraphStyle("Footer", parent=styles["Normal"],
                                      fontSize=8, textColor=colors.grey)
        story.append(Paragraph(
            "Generated by elec-agent — open source — MIT License — github.com/yourname/elec-agent",
            footer_style
        ))
        story.append(Paragraph(
            "⚠ This report is an assistance tool. Only a qualified electrician can certify "
            "electrical installation compliance.",
            footer_style
        ))

        # Build PDF
        doc.build(story)
