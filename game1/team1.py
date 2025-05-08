import questionary
from rich.console import Console
from database.database import Database, get_game1_terms, update_game1_term
from .shared import calculate_game1_outputs, display_game1_outputs

console = Console()
db = Database()


def main():
    console.print("[bold blue]\n=== Simulation Game 1 - Team 1 ===\n")

    # Initial input collection
    with db.get_conn() as conn:
        terms = get_game1_terms(conn)
        for term in terms:
            if term[2] is None:
                value = questionary.text(
                    f"Enter value for {term[1]} ({term[4]}):",
                    validate=lambda x: x.replace('.', '').isdigit()
                ).ask()
                update_game1_term(conn, term[1], 1, float(value))

        # Main interaction loop
        while True:
            outputs = calculate_game1_outputs(conn)
            display_game1_outputs(outputs)

            if outputs['all_approved']:
                console.print("[bold green]\nAll terms agreed! Simulation complete.")
                return

            action = questionary.select(
                "What would you like to do?",
                choices=[
                    {"name": "Edit a term", "value": "edit"},
                    {"name": "Exit", "value": "exit"}
                ]
            ).ask()

            if action == "exit":
                return

            term_to_edit = questionary.select(
                "Which term would you like to edit?",
                choices=[
                    {
                        "name": f"{term[1]} (current: {term[2] or 'not set'})",
                        "value": term[1]
                    }
                    for term in terms
                ]
            ).ask()

            new_value = questionary.text(
                f"Enter new value for {term_to_edit}:",
                validate=lambda x: x.replace('.', '').isdigit()
            ).ask()

            update_game1_term(conn, term_to_edit, 1, float(new_value))
            console.print(f"[yellow]\n{term_to_edit} updated. Team 2 will need to re-approve this term.")


if __name__ == "__main__":
    main()