from rich.console import Console
from rich.table import Table

console = Console()


def calculate_game2_outputs(conn):
    """
    Calculate all investor metrics based on company data
    Returns dictionary with all calculated values
    """
    with conn.cursor() as cur:
        # Get all company prices and shares
        cur.execute("""
            SELECT 
                MAX(CASE WHEN term = 'price_company1' THEN team1_company1 END) as price1,
                MAX(CASE WHEN term = 'price_company2' THEN team1_company2 END) as price2,
                MAX(CASE WHEN term = 'price_company3' THEN team1_company3 END) as price3,
                MAX(CASE WHEN term = 'shares_company1' THEN team1_company1 END) as shares1,
                MAX(CASE WHEN term = 'shares_company2' THEN team1_company2 END) as shares2,
                MAX(CASE WHEN term = 'shares_company3' THEN team1_company3 END) as shares3
            FROM game2_terms
        """)

        prices = cur.fetchone()
        if not any(prices):
            raise ValueError("No company data found in database")

        price1, price2, price3, shares1, shares2, shares3 = prices

        # Calculate metrics
        results = {
            # Market Capitalization (Price * Shares)
            "market_cap_company1": price1 * shares1,
            "market_cap_company2": price2 * shares2,
            "market_cap_company3": price3 * shares3,

            # Total Market Value
            "total_market_value": (price1 * shares1) + (price2 * shares2) + (price3 * shares3),

            # Company Weightings
            "weight_company1": (price1 * shares1) / (price1 * shares1 + price2 * shares2 + price3 * shares3),
            "weight_company2": (price2 * shares2) / (price1 * shares1 + price2 * shares2 + price3 * shares3),
            "weight_company3": (price3 * shares3) / (price1 * shares1 + price2 * shares2 + price3 * shares3),

            # Investor Metrics
            "investment_per_share": {
                "company1": price1 * 1.10,  # 10% premium
                "company2": price2 * 1.10,
                "company3": price3 * 1.10
            },

            "profit_potential": {
                "company1": (price1 * 1.15 - price1) * shares1,  # 15% growth assumption
                "company2": (price2 * 1.15 - price2) * shares2,
                "company3": (price3 * 1.15 - price3) * shares3
            }
        }

        return results


def display_game2_outputs(data):
    """Display all calculated metrics in rich tables"""

    # Main Metrics Table
    main_table = Table(title="Game 2 - Market Overview", show_header=True, header_style="bold magenta")
    main_table.add_column("Metric", style="cyan")
    main_table.add_column("Company 1", justify="right")
    main_table.add_column("Company 2", justify="right")
    main_table.add_column("Company 3", justify="right")

    main_table.add_row(
        "Share Price ($)",
        f"${data['price_company1']:,.2f}",
        f"${data['price_company2']:,.2f}",
        f"${data['price_company3']:,.2f}"
    )
    main_table.add_row(
        "Shares Available",
        f"{data['shares_company1']:,}",
        f"{data['shares_company2']:,}",
        f"{data['shares_company3']:,}"
    )
    main_table.add_row(
        "Market Cap ($)",
        f"${data['market_cap_company1']:,.2f}",
        f"${data['market_cap_company2']:,.2f}",
        f"${data['market_cap_company3']:,.2f}"
    )
    main_table.add_row(
        "Market Weight",
        f"{data['weight_company1']:.2%}",
        f"{data['weight_company2']:.2%}",
        f"{data['weight_company3']:.2%}"
    )

    console.print(main_table)

    # Investment Recommendations Table
    invest_table = Table(title="Investment Recommendations", show_header=True, header_style="bold green")
    invest_table.add_column("Metric", style="cyan")
    invest_table.add_column("Company 1", justify="right")
    invest_table.add_column("Company 2", justify="right")
    invest_table.add_column("Company 3", justify="right")

    invest_table.add_row(
        "Investment/Share ($)",
        f"${data['investment_per_share']['company1']:,.2f}",
        f"${data['investment_per_share']['company2']:,.2f}",
        f"${data['investment_per_share']['company3']:,.2f}"
    )
    invest_table.add_row(
        "Profit Potential ($)",
        f"${data['profit_potential']['company1']:,.2f}",
        f"${data['profit_potential']['company2']:,.2f}",
        f"${data['profit_potential']['company3']:,.2f}"
    )

    console.print(invest_table)

    # Summary Statistics
    console.print(f"\n[bold]Total Market Value:[/bold] ${data['total_market_value']:,.2f}")
    console.print("[yellow]Note:[/yellow] Investment prices include 10% premium, profit potential assumes 15% growth")


def get_game2_terms(conn):
    """Utility function to fetch all game2 terms"""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM game2_terms")
        return cur.fetchall()


if __name__ == "__main__":
    from database.database import Database

    db = Database()
    with db.get_conn() as conn:
        data = calculate_game2_outputs(conn)
        display_game2_outputs(data)