# ⚡ elec-agent CLI
# Usage: elec-agent analyze <schematic.png> --output rapport.pdf -v

import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from .agent import ElecAgent

console = Console()


@click.group()
def app():
    """elec-agent — Autonomous NF C 15-100 electrical schematic analyzer."""
    pass


@app.command()
@click.argument("schematic", type=click.Path(exists=True))
@click.option("--config", "-c", default="config.yaml", help="Configuration file path")
@click.option("--output", "-o", default="rapport.pdf", help="Output PDF report path")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed error messages")
def analyze(schematic, config, output, verbose):
    """
    Analyze an electrical schematic for NF C 15-100 compliance.
    
    Example:
        elec-agent analyze schema.png --output rapport.pdf -v
    """
    schematic_path = Path(schematic)

    console.print(Panel(
        "[bold yellow]⚡ elec-agent[/bold yellow] — NF C 15-100 Compliance Check",
        expand=False
    ))

    # Initialize agent with config
    agent = ElecAgent(config_path=Path(config), verbose=verbose)

    # Step 1: Extract components using vision LLM
    with console.status("[bold green]Extracting components via vision LLM...[/bold green]"):
        components = agent.extract_components(schematic_path)

    console.print(f"[green]✓[/green] {len(components)} components detected")

    # Step 2: Check NF C 15-100 rules
    with console.status("[bold green]Checking NF C 15-100 rules...[/bold green]"):
        issues = agent.check_rules(components)

    # Count errors and warnings
    errors   = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]

    console.print(f"[red]✗[/red] {len(errors)} errors  [yellow]⚠[/yellow] {len(warnings)} warnings")

    # Show detailed issues if verbose mode
    if verbose:
        for issue in issues:
            color = "red" if issue["severity"] == "error" else "yellow"
            console.print(f"  [{color}]{issue['severity'].upper()}[/{color}] {issue['message']}")

    # Step 3: Generate PDF report
    with console.status("[bold green]Generating PDF report...[/bold green]"):
        agent.generate_report(components, issues, Path(output))

    console.print(f"[bold green]✓ Report generated:[/bold green] {output}")


if __name__ == "__main__":
    app()