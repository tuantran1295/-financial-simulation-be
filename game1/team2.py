import questionary
from rich.console import Console
from rich.table import Table
from database import Database, get_game1_terms, update_game1_term
from time import sleep
import os

console = Console()
db = Database()


def display_game1_terms(terms):
    """Display current terms with approval status"""
    table = Table(title="[bold cyan]Current Terms (Team 2 View)")
    table.add_column("Term", style="magenta")
    table.add_column("Team 1 Value", style="green")
    table.add_column("Your Approval", justify="right")

    for term in terms:
        approval_status = (
            "[green]✓" if term[3] else
            "[yellow]PENDING" if term[2] else
            "[red]NOT SET"
        )
        table.add_row(
            f"{term[1]} ({term[4]})",
            str(term[2]) if term[2] is not None else "-",
            approval_status
        )

    console.print(table)


def calculate_valuation(terms):
    """Calculate final valuation if all terms are approved"""
    if all(term[3] for term in terms):
        term_values = {term[1]: term[2] for term in terms}
        valuation = (
                term_values['EBITDA'] *
                term_values['Multiple'] *
                term_values['Factor Score']
        )
        console.print(f"\n[bold green]VALUATION: ${valuation:,.2f}[/]")
        return valuation
    else:
        pending_terms = [term[1] for term in terms if not term[3] and term[2] is not None]
        if pending_terms:
            console.print(f"\n[yellow]Pending approvals: {', '.join(pending_terms)}[/]")
        return None


def main():
    console.print("[bold blue]\n=== Simulation Game 1 - Team 2 (Approvals) ===")
    console.print("[italic]You will approve/reject valuation terms from Team 1\n")

    with db.get_conn() as conn:
        while True:
            # Clear screen for fresh display
            os.system('cls' if os.name == 'nt' else 'clear')

            # Get current terms
            terms = get_game1_terms(conn)

            # Display current state
            display_game1_terms(terms)
            valuation = calculate_valuation(terms)

            # Exit if all terms are approved
            if valuation is not None:
                console.print("\n[bold green]All terms approved! Simulation complete.")
                break

            # Get user action
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    {"name": "Review term for approval", "value": "approve"},
                    {"name": "Refresh view", "value": "refresh"},
                    {"name": "Exit", "value": "exit"}
                ]
            ).ask()

            if action == "exit":
                break
            elif action == "refresh":
                continue

            # Select term to review
            term_to_review = questionary.select(
                "Select term to approve/reject:",
                choices=[
                    {
                        "name": f"{term[1]} (Value: {term[2] or 'Not set'})",
                        "value": term[1]
                    }
                    for term in terms
                    if term[2] is not None and not term[3]
                ]
            ).ask()

            # Get approval decision
            decision = questionary.select(
                f"Approve {term_to_review} = {next(t[2] for t in terms if t[1] == term_to_review)}?",
                choices=[
                    {"name": "Approve", "value": True},
                    {"name": "Reject (send back to Team 1)", "value": False}
                ]
            ).ask()

            # Update database
            update_game1_term(conn, term_to_review, 2, decision)

            if decision:
                console.print(f"[green]✓ Approved {term_to_review}!")
            else:
                console.print(f"[yellow]↑ Sent {term_to_review} back to Team 1 for revision")

            sleep(1)  # Brief pause for user to see feedback


if __name__ == "__main__":
    main()