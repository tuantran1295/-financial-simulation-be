import sys
from rich.console import Console
from database.database import Database, update_game2_term

console = Console()
db = Database()


def collect_company_data():
    """Collect and validate company inputs"""
    companies = {}

    for i in range(1, 4):  # For 3 companies
        while True:
            try:
                console.print(f"[bold]\nCompany {i} Data[/bold]")
                price = float(console.input(f"? Enter share price ($) for Company {i}: "))
                shares = int(console.input(f"? Enter shares available for Company {i}: "))

                if price <= 0 or shares <= 0:
                    console.print("[red]Error: Values must be positive")
                    continue

                companies[f"Company{i}"] = {
                    "price": price,
                    "shares": shares
                }
                break
            except ValueError:
                console.print("[red]Error: Please enter valid numbers")

    return companies


def save_to_database(companies):
    """Save company data to database using your Database class"""
    with db.get_conn() as conn:
        # Save prices (Team 1 = team1)
        update_game2_term(conn, f"price_company1", 1, 1, companies["Company1"]["price"])
        update_game2_term(conn, f"price_company2", 1, 2, companies["Company2"]["price"])
        update_game2_term(conn, f"price_company3", 1, 3, companies["Company3"]["price"])

        # Save shares (Team 1 = team1)
        update_game2_term(conn, f"shares_company1", 1, 1, companies["Company1"]["shares"])
        update_game2_term(conn, f"shares_company2", 1, 2, companies["Company2"]["shares"])
        update_game2_term(conn, f"shares_company3", 1, 3, companies["Company3"]["shares"])


def main():
    console.print("[bold blue]=== Game 2 - Team 1 (Companies) ===")
    companies = collect_company_data()
    save_to_database(companies)
    console.print("[green bold]✓ All company data saved successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[red]Error: {e}")
        sys.exit(1)