"""
Main entry point for Luma AI Assistant
"""

import typer
from rich.console import Console
from .core import Luma
from .web import run_web

app = typer.Typer()
console = Console()

@app.command()
def cli():
    """
    Start Luma AI Assistant in command-line mode
    """
    try:
        luma = Luma()
        luma.run()
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise typer.Exit(1)

@app.command()
def web():
    """
    Start Luma AI Assistant with web interface
    """
    try:
        run_web()
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app() 