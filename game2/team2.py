import sys
from rich.console import Console
from database.database import Database
from game2.shared import calculate_game2_outputs, display_game2_outputs

console = Console()
db = Database()


def verify_team1_completion(conn):
    """Check if Team 1 completed all required inputs"""
    required_terms = [
        "price_company1", "price_company2", "price_company3",
        "shares_company1", "shares_company2", "shares_company3"
    ]

    with conn.cursor() as cur:
        cur.execute("""
            SELECT term FROM game2_terms
            WHERE term = ANY(%s) AND (team1_company1 IS NULL OR 
                                     team1_company2 IS NULL OR 
                                     team1_company3 IS NULL)
        """, (required_terms,))

        missing = cur.fetchall()
        if missing:
            console.print("[red]Error: Missing Team 1 inputs for:")
            for term in missing:
                console.print(f"  - {term[0]}")
            return False
        return True


def main():
    console.print("[bold blue]=== Game 2 - Team 2 (Investors) ===")

    with db.get_conn() as conn:
        # Step 1: Verify Team 1 completed their inputs
        if not verify_team1_completion(conn):
            sys.exit(1)

        # Step 2: Perform calculations
        try:
            data = calculate_game2_outputs(conn)
            display_game2_outputs(data)
        except Exception as e:
            console.print(f"[red]Calculation error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()