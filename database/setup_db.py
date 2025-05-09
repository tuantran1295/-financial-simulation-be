import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from rich.console import Console

console = Console()


def create_database():
    """Create the database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="root-1234567890",
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname='simulation_games'")
        exists = cur.fetchone()

        if not exists:
            cur.execute("CREATE DATABASE simulation_games")
            console.print("[green]✓ Database created successfully")
        else:
            console.print("[yellow]Database already exists")

        cur.close()
        conn.close()
    except Exception as e:
        console.print(f"[red]Error creating database: {e}")
        raise


def initialize_tables():
    """Initialize all tables with proper schema for both games"""
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="root-1234567890",
            host="localhost",
            port="5432",
            database="simulation_games"
        )
        conn.autocommit = True
        cur = conn.cursor()

        # ===== Game 1 Tables =====
        cur.execute("""
        CREATE TABLE IF NOT EXISTS game1_terms (
            id SERIAL PRIMARY KEY,
            term VARCHAR(50) UNIQUE NOT NULL,
            team1_value NUMERIC,
            team2_approval BOOLEAN DEFAULT FALSE,
            description TEXT,
            last_updated TIMESTAMP DEFAULT NOW()
        )""")

        # Insert CRITICAL DEFAULT TERMS for Game 1
        cur.execute("""
        INSERT INTO game1_terms (term, description)
        VALUES 
            ('EBITDA', 'Earnings Before Interest, Taxes, Depreciation, and Amortization'),
            ('Multiple', 'Industry-standard valuation multiplier'),
            ('Factor Score', 'Company-specific adjustment factor (0.5 - 1.5)')
        ON CONFLICT (term) DO UPDATE SET 
            description = EXCLUDED.description""")
        console.print("[green]✓ Game 1 terms initialized")

        # ===== Game 2 Tables =====
        cur.execute("""
        CREATE TABLE IF NOT EXISTS game2_terms (
            id SERIAL PRIMARY KEY,
            term VARCHAR(50) NOT NULL,
            team1_company1 NUMERIC,
            team1_company2 NUMERIC,
            team1_company3 NUMERIC,
            team2_company1 NUMERIC,
            team2_company2 NUMERIC,
            team2_company3 NUMERIC,
            last_updated TIMESTAMP DEFAULT NOW(),
            UNIQUE(term)
        )""")

        cur.execute("""
        INSERT INTO game2_terms (term)
        VALUES 
            ('price_company1'), ('price_company2'), ('price_company3'),
            ('shares_company1'), ('shares_company2'), ('shares_company3'),
            ('investor1_budget'), ('investor2_budget'), ('investor3_budget')
        ON CONFLICT (term) DO NOTHING""")
        console.print("[green]✓ Game 2 terms initialized")

        # Create results tables
        cur.execute("""
        CREATE TABLE IF NOT EXISTS game2_results (
            id SERIAL PRIMARY KEY,
            calculation_time TIMESTAMP DEFAULT NOW(),
            total_market_value NUMERIC,
            company1_weight NUMERIC,
            company2_weight NUMERIC,
            company3_weight NUMERIC
        )""")

        cur.close()
        conn.close()
    except Exception as e:
        console.print(f"[red]Error initializing tables: {e}")
        raise


def verify_setup():
    """Verify both Game 1 and Game 2 setups"""
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="root-1234567890",
            host="localhost",
            port="5432",
            database="simulation_games"
        )
        cur = conn.cursor()
        verified = True

        # Verify Game 1
        cur.execute("SELECT term FROM game1_terms")
        game1_terms = {row[0] for row in cur.fetchall()}
        required_game1 = {'EBITDA', 'Multiple', 'Factor Score'}

        if not required_game1.issubset(game1_terms):
            missing = required_game1 - game1_terms
            console.print(f"[red]Missing Game 1 terms: {', '.join(missing)}")
            verified = False

        # Verify Game 2
        cur.execute("""
        SELECT term FROM game2_terms 
        WHERE term LIKE 'price_%' OR term LIKE 'shares_%'
        """)
        game2_terms = {row[0] for row in cur.fetchall()}
        required_game2 = {
            'price_company1', 'price_company2', 'price_company3',
            'shares_company1', 'shares_company2', 'shares_company3'
        }

        if not required_game2.issubset(game2_terms):
            missing = required_game2 - game2_terms
            console.print(f"[red]Missing Game 2 terms: {', '.join(missing)}")
            verified = False

        if verified:
            console.print("[green]✓ Both Game 1 and Game 2 verified successfully")
        return verified

    except Exception as e:
        console.print(f"[red]Verification failed: {e}")
        return False
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    console.print("[bold cyan]\n=== Database Setup ===")

    try:
        console.print("\n[bold]1. Database Creation")
        create_database()

        console.print("\n[bold]2. Table Initialization")
        initialize_tables()

        console.print("\n[bold]3. Schema Verification")
        if verify_setup():
            console.print("\n[bold green]✓ Setup completed successfully!")
        else:
            console.print("\n[bold red]! Setup verification failed")
            raise RuntimeError("Verification failed")

    except Exception as e:
        console.print(f"\n[bold red]Fatal error during setup: {e}")
        console.print("Try resetting the database manually:")
        console.print("1. psql -U postgres")
        console.print("2. DROP DATABASE simulation_games;")
        console.print("3. CREATE DATABASE simulation_games;")
        exit(1)