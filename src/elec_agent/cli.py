# ⚡ elec-agent CLI
# Usage: elec-agent analyze <schematic.png> --output rapport.pdf -v

import typer
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from .agent import ElecAgent

# Main app with invoke_without_command=True so bare "elec-agent" still shows help
app = typer.Typer(
    name="elec-agent",
    help="Autonomous NF C 15-100 electrical schematic analyzer.",
    add_completion=False,
)
console = Console()


@app.command("analyze")
def analyze(
    schematic: Path = typer.Argument(
        ...,
        help="Path to schematic image or PDF file"
    ),
    config: Path = typer.Option(
        "config.yaml",
        help="Configuration file path (LLM settings, rules, output format)"
    ),
    output: Path = typer.Option(
        "rapport.pdf",
        help="Output PDF report path"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed error messages"
    ),
):
    """
    Analyze an electrical schematic for NF C 15-100 compliance.

    Example:
        elec-agent analyze schema.png --output rapport.pdf -v
    """
    console.print(Panel(
        "[bold yellow]⚡ elec-agent[/bold yellow] — NF C 15-100 Compliance Check",
        expand=False
    ))

    # Validate input file exists
    if not schematic.exists():
        console.print(f"[red]Error:[/red] file not found: {schematic}")
        raise typer.Exit(1)

    # Initialize agent with config
    agent = ElecAgent(config_path=config, verbose=verbose)

    # Step 1: Extract components using vision LLM
    with console.status("[bold green]Extracting components via vision LLM...[/bold green]"):
        components = agent.extract_components(schematic)

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
        agent.generate_report(components, issues, output)

    console.print(f"[bold green]✓ Report generated:[/bold green] {output}")


if __name__ == "__main__":
    app()
