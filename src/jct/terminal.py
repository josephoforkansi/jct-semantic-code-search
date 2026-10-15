"""Rich terminal interface for JCT semantic code search."""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
)
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

console = Console()

QUERY_COLORS = [
    "bright_green",
    "bright_yellow",
    "bright_magenta",
    "bright_blue",
    "bright_red",
]


def _copy_to_clipboard(code: str) -> bool:
    """Copy text to the system clipboard when a clipboard utility is available."""
    if sys.platform == "win32":
        commands = [["clip"]]
    elif sys.platform == "darwin":
        commands = [["pbcopy"]]
    else:
        commands = [
            ["wl-copy"],
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
        ]

    for command in commands:
        try:
            result = subprocess.run(
                command,
                input=code,
                text=True,
                capture_output=True,
                check=False,
            )
        except (FileNotFoundError, OSError):
            continue

        if result.returncode == 0:
            return True

    return False


def display_code(
    code: str,
    title: str = "PYTHON CODE",
    language: str = "python",
    interactive_copy: bool = True,
) -> None:
    """Display syntax-highlighted code and optionally offer clipboard copying."""
    if not code.strip():
        return

    clean_code = code.rstrip()

    syntax = Syntax(
        clean_code,
        language,
        theme="monokai",
        line_numbers=True,
        word_wrap=True,
        indent_guides=True,
    )

    console.print(
        Panel(
            syntax,
            title=f"[bold green]{title}[/bold green]",
            border_style="green",
            padding=(1, 2),
        )
    )

    # Do not prompt when output is redirected or the command is noninteractive.
    if not interactive_copy:
        return

    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return

    console.print(
        "[dim]Press C to copy this code, or press Enter to continue.[/dim]"
    )

    try:
        choice = input("> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print()
        return

    if choice == "c":
        if _copy_to_clipboard(clean_code):
            console.print(
                "[bold bright_green]SUCCESS[/bold bright_green] "
                "Code copied to the clipboard."
            )
        else:
            console.print(
                "[bold yellow]Clipboard unavailable.[/bold yellow] "
                "Select the code above and copy it manually."
            )


def display_markdown_with_code(
    answer: str,
    interactive_copy: bool = True,
) -> None:
    """Render Markdown responses and syntax-highlight fenced code blocks."""
    if not answer.strip():
        console.print("[yellow]The response was empty.[/yellow]")
        return

    # Match Markdown fenced blocks such as ```python ... ```.
    pattern = re.compile(
        r"```([^\n`]*)\n(.*?)```",
        flags=re.DOTALL,
    )

    position = 0

    for match in pattern.finditer(answer):
        preceding_text = answer[position:match.start()]

        if preceding_text.strip():
            console.print(Markdown(preceding_text))

        language = match.group(1).strip() or "python"
        code = match.group(2)

        display_code(
            code,
            title=f"CODE EXAMPLE ({language.upper()})",
            language=language,
            interactive_copy=interactive_copy,
        )

        position = match.end()

    remaining_text = answer[position:]

    if remaining_text.strip():
        console.print(Markdown(remaining_text))


def display_banner() -> None:
    """Display the JCT welcome banner."""
    logo = Text()

    logo.append("       J C T\n", style="bold bright_cyan")
    logo.append("  JOSEPH COOL TOOL\n", style="bold white")
    logo.append(
        "Semantic Search for Python Code\n\n",
        style="bright_cyan",
    )
    logo.append(
        "Find code by what it DOES,\n",
        style="bold white",
    )
    logo.append(
        "not just what it says.",
        style="italic bright_magenta",
    )

    console.print()
    console.print(
        Panel(
            logo,
            border_style="bright_blue",
            box=box.DOUBLE,
            padding=(1, 4),
        )
    )
    console.print(
        "[dim]Search smarter. Discover behavior. Explore code.[/dim]\n"
    )


def display_main_menu() -> None:
    """Display the main application menu."""
    table = Table(
        title="[bold bright_cyan]MAIN MENU[/bold bright_cyan]",
        box=box.ROUNDED,
        border_style="bright_blue",
        show_header=False,
        padding=(0, 2),
        expand=True,
    )

    table.add_column("Choice", style="bold bright_yellow", width=10)
    table.add_column("Action", style="white")

    table.add_row("[1]", "Search a Python project")
    table.add_row("[2]", "Search a ZIP archive")
    table.add_row("[3]", "Choose another source")
    table.add_row("[4]", "Help and search tips")
    table.add_row("[5]", "Configure search settings")
    table.add_row("[Q]", "Quit JCT")

    console.print(table)


def display_source_menu() -> None:
    """Display source-selection options."""
    table = Table(
        title="[bold bright_cyan]CHOOSE YOUR SOURCE[/bold bright_cyan]",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=False,
        expand=True,
    )

    table.add_column("Choice", style="bold bright_yellow", width=10)
    table.add_column("Source", style="white")

    table.add_row("[1]", "Use the current directory")
    table.add_row("[2]", "Enter a project folder path")
    table.add_row("[3]", "Enter a ZIP archive path")
    table.add_row("[B]", "Go back")

    console.print(table)


def display_original_query(query: str) -> None:
    """Display the original query in a cyan panel."""
    console.print(
        Panel(
            Text(query, style="bold white"),
            title="[bold bright_cyan]YOUR SEARCH[/bold bright_cyan]",
            border_style="bright_cyan",
            padding=(1, 2),
        )
    )


def display_reformulated_queries(
    queries: Sequence[str],
) -> None:
    """Display alternative queries with consistent colors."""
    console.print(
        "\n[bold bright_cyan]SMART QUERY SUGGESTIONS[/bold bright_cyan]"
    )

    if not queries:
        console.print(
            "[yellow]No alternative queries were generated.[/yellow]"
        )
        return

    for index, query in enumerate(queries, start=1):
        color = QUERY_COLORS[(index - 1) % len(QUERY_COLORS)]

        line = Text()
        line.append(f"  [{index}] ", style=f"bold {color}")
        line.append(query, style=color)

        console.print(line)


def display_search_strategy_menu() -> None:
    """Display available query-selection strategies."""
    console.print()
    console.print("[bold white]HOW WOULD YOU LIKE TO SEARCH?[/bold white]")
    console.print("  [bold bright_yellow]0[/bold bright_yellow]  Use my original query")
    console.print("  [bold bright_yellow]A[/bold bright_yellow]  Automatically combine suggestions")
    console.print("  [bold bright_yellow]M[/bold bright_yellow]  Manually select multiple suggestions")
    console.print("  [bold bright_yellow]B[/bold bright_yellow]  Go back")


def display_source_info(source: str | Path) -> None:
    """Display the selected project or archive."""
    console.print(
        Panel(
            str(Path(source).expanduser().resolve()),
            title="[bold green]ACTIVE SOURCE[/bold green]",
            border_style="green",
        )
    )


def display_search_progress(
    message: str = "Searching Python code...",
) -> Progress:
    """Create a Rich progress display for longer operations."""
    return Progress(
        SpinnerColumn(style="bright_cyan"),
        TextColumn("[bold bright_cyan]{task.description}"),
        BarColumn(),
        TextColumn("[dim]{task.completed}/{task.total}"),
        console=console,
        transient=True,
    )


def display_search_status(message: str) -> None:
    """Display an informational status message."""
    console.print(f"[bold bright_cyan]JCT[/bold bright_cyan]  {message}")


def display_success(message: str) -> None:
    """Display a success message."""
    console.print(
        f"[bold bright_green]SUCCESS[/bold bright_green]  {message}"
    )


def display_warning(message: str) -> None:
    """Display a warning message."""
    console.print(
        f"[bold bright_yellow]WARNING[/bold bright_yellow]  {message}"
    )


def display_error(message: str) -> None:
    """Display an error message."""
    console.print(
        f"[bold bright_red]ERROR[/bold bright_red]  {message}"
    )


def display_no_results(query: str, min_score: float) -> None:
    """Explain why a search returned no results."""
    message = Text()

    message.append("No code matched your query above the threshold.\n\n")
    message.append("Query: ", style="bold")
    message.append(f"{query}\n")
    message.append("Minimum score: ", style="bold")
    message.append(f"{min_score:.3f}\n\n")
    message.append(
        "Try a different query, lower the threshold, "
        "or consider the AI fallback."
    )

    console.print(
        Panel(
            message,
            title="[bold yellow]NO MATCHES FOUND[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )


def display_results_table(
    results: list[dict[str, Any]],
    query: str | None = None,
) -> None:
    """Display ranked search results in a readable table."""
    if query:
        console.print()
        display_original_query(query)

    if not results:
        display_warning("No results to display.")
        return

    table = Table(
        title="[bold bright_green]SEARCH RESULTS[/bold bright_green]",
        box=box.ROUNDED,
        border_style="bright_green",
        header_style="bold bright_cyan",
        show_lines=True,
        expand=True,
    )

    table.add_column("#", justify="right", width=4)
    table.add_column("Score", justify="right", width=8)
    table.add_column("Symbol", style="bright_white", min_width=16)
    table.add_column("Location", style="cyan", min_width=20)

    for rank, result in enumerate(results, start=1):
        score = float(result.get("score", 0.0))
        name = str(result.get("name", "<unnamed>"))
        kind = str(result.get("type", "code")).capitalize()
        filename = str(result.get("file", "<unknown>"))
        line = result.get("start_line", "?")

        if score >= 0.80:
            score_style = "bold bright_green"
        elif score >= 0.65:
            score_style = "bright_yellow"
        else:
            score_style = "white"

        table.add_row(
            str(rank),
            f"[{score_style}]{score:.3f}[/{score_style}]",
            f"{kind} {name}",
            f"{filename}:{line}",
        )

    console.print(table)
    console.print(
        f"[dim]Showing {len(results)} ranked result(s).[/dim]"
    )


def display_result_details(
    result: dict[str, Any],
    rank: int | None = None,
) -> None:
    """Display the complete details of a selected result."""
    heading = "RESULT DETAILS"

    if rank is not None:
        heading = f"RESULT #{rank} DETAILS"

    name = str(result.get("name", "<unnamed>"))
    kind = str(result.get("type", "code")).capitalize()
    filename = str(result.get("file", "<unknown>"))
    line = result.get("start_line", "?")
    score = float(result.get("score", 0.0))
    code = str(result.get("code", ""))
    docstring = str(result.get("docstring", ""))

    details = Table.grid(padding=(0, 1))
    details.add_column(style="bold bright_cyan", width=12)
    details.add_column(style="white")

    details.add_row("Name", f"{kind} {name}")
    details.add_row("Location", f"{filename}:{line}")
    details.add_row("Score", f"{score:.3f}")

    console.print(
        Panel(
            details,
            title=f"[bold bright_cyan]{heading}[/bold bright_cyan]",
            border_style="bright_cyan",
        )
    )

    if docstring:
        console.print(
            Panel(
                docstring,
                title="[bold magenta]DESCRIPTION[/bold magenta]",
                border_style="magenta",
            )
        )

    if code:
        display_code(
            code,
            title="PYTHON CODE",
            language="python",
        )


def display_results_menu() -> None:
    """Display actions available after searching."""
    console.print()
    console.print("[bold white]WHAT NEXT?[/bold white]")
    console.print("  [bold bright_yellow]1[/bold bright_yellow]  View a result")
    console.print("  [bold bright_yellow]2[/bold bright_yellow]  Search again")
    console.print("  [bold bright_yellow]3[/bold bright_yellow]  Change the similarity threshold")
    console.print("  [bold bright_yellow]4[/bold bright_yellow]  Choose another project")
    console.print("  [bold bright_yellow]5[/bold bright_yellow]  Return to the main menu")
    console.print("  [bold bright_yellow]Q[/bold bright_yellow]  Quit")


def display_help() -> None:
    """Display user-friendly search instructions."""
    help_text = (
        "[bold bright_cyan]HOW TO SEARCH WITH JCT[/bold bright_cyan]\n\n"
        "Describe the behavior you want to find, not just a "
        "specific function name.\n\n"
        "[bold green]Good examples[/bold green]\n"
        "  - Find code that safely reads a file.\n"
        "  - Find functions that validate user input.\n"
        "  - Find code that catches exceptions.\n"
        "  - Find a function that sorts a list.\n"
        "  - Find code that saves data to a JSON file.\n\n"
        "[bold yellow]Tips[/bold yellow]\n"
        "  - Describe the desired behavior clearly.\n"
        "  - Try suggested queries when results are weak.\n"
        "  - A lower threshold may return more matches.\n"
        "  - AI-generated fallback responses are not retrieved code "
        "and must be verified."
    )

    console.print(
        Panel(
            Markdown(help_text),
            title="[bold bright_cyan]JCT HELP[/bold bright_cyan]",
            border_style="bright_blue",
            padding=(1, 2),
        )
    )


def display_original_and_alternatives(
    original_query: str,
    alternatives: Sequence[str],
) -> None:
    """Display the original query and its alternatives."""
    display_original_query(original_query)
    display_reformulated_queries(alternatives)


if __name__ == "__main__":
    display_banner()
    display_main_menu()
