from rich.table import Table
from rich.console import Console
from database.database import get_game1_terms

console = Console()


def calculate_game1_outputs(conn):
    terms = get_game1_terms(conn)
    outputs = {
        'team1': {},
        'team2': {},
        'common': {'valuation': None},
        'all_approved': True
    }

    term_values = {}

    for term in terms:
        outputs['team1'][term[1]] = 'OK' if term[3] else 'TBD'
        outputs['team2'][term[1]] = term[2]

        if not term[3]:
            outputs['all_approved'] = False

        term_values[term[1]] = term[2]

    if outputs['all_approved']:
        outputs['common']['valuation'] = (
                term_values['EBITDA'] *
                term_values['Multiple'] *
                term_values['Factor Score']
        )
    else:
        outputs['common']['valuation'] = 'Not yet agreed by Team 2'

    return outputs


def display_game1_outputs(outputs):
    table = Table(title="Game 1 - Current Outputs")
    table.add_column("Term", style="cyan")
    table.add_column("Team 1 Status", style="magenta")
    table.add_column("Team 2 Value", style="green")

    for term, status in outputs['team1'].items():
        table.add_row(
            term,
            f"[green]{status}" if status == "OK" else f"[yellow]{status}",
            str(outputs['team2'][term])
        )

    console.print(table)

    valuation_text = (
        f"[bold green]${outputs['common']['valuation']:,.2f}"
        if isinstance(outputs['common']['valuation'], (int, float))
        else f"[yellow]{outputs['common']['valuation']}"
    )
    console.print(f"\n[b]Valuation:[/b] {valuation_text}\n")