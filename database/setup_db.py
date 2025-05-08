import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from rich.console import Console

console = Console()


def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres DB
        conn = psycopg2.connect(
            user="postgres",
            password="root-1234567890",
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname='simulation_games'")
        exists = cur.fetchone()

        if not exists:
            cur.execute("CREATE DATABASE simulation_games")
            console.print("[green]✓ Database 'simulation_games' created successfully")
        else:
            console.print("[yellow]Database 'simulation_games' already exists")

        cur.close()
        conn.close()
    except Exception as e:
        console.print(f"[red]Error creating database: {e}")
        raise


def initialize_tables():
    """Initialize all required tables with default data"""
    try:
        # Connect to our database
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
        )
        """)

        # Insert default terms for Game 1
        cur.execute("""
        INSERT INTO game1_terms (term, description)
        VALUES 
            ('EBITDA', 'Earnings Before Interest, Taxes, Depreciation, and Amortization'),
            ('Multiple', 'Industry-standard valuation multiplier'),
            ('Factor Score', 'Company-specific adjustment factor (0.5 - 1.5)')
        ON CONFLICT (term) DO NOTHING
        """)

        # ===== Game 2 Tables =====
        cur.execute("""
        CREATE TABLE IF NOT EXISTS game2_terms (
            id SERIAL PRIMARY KEY,
            term VARCHAR(50) UNIQUE NOT NULL,
            team1_company1 NUMERIC,
            team1_company2 NUMERIC,
            team1_company3 NUMERIC,
            team2_company1 NUMERIC,
            team2_company2 NUMERIC,
            team2_company3 NUMERIC,
            last_updated TIMESTAMP DEFAULT NOW()
        )
        """)

        # Insert default terms for Game 2
        cur.execute("""
        INSERT INTO game2_terms (term)
        VALUES 
            ('Price'),
            ('Shares'),
            ('Investor 1'), 
            ('Investor 2'),
            ('Investor 3')
        ON CONFLICT (term) DO NOTHING
        """)

        console.print("[green]✓ Tables initialized successfully with default data")

        # Verify table creation
        cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        console.print(f"[blue]Existing tables: {', '.join([t[0] for t in tables])}")

        cur.close()
        conn.close()
    except Exception as e:
        console.print(f"[red]Error initializing tables: {e}")
        raise


def verify_setup():
    """Verify the database setup was successful"""
    try:
        conn = psycopg2.connect(
            user="postgres",
            password="root-1234567890",
            host="localhost",
            port="5432",
            database="simulation_games"
        )
        cur = conn.cursor()

        # Check Game 1 terms
        cur.execute("SELECT COUNT(*) FROM game1_terms")
        game1_count = cur.fetchone()[0]
        console.print(f"[blue]Game 1 terms: {game1_count} records")

        # Check Game 2 terms
        cur.execute("SELECT COUNT(*) FROM game2_terms")
        game2_count = cur.fetchone()[0]
        console.print(f"[blue]Game 2 terms: {game2_count} records")

        cur.close()
        conn.close()

        if game1_count >= 3 and game2_count >= 5:
            console.print("[green]✓ Database verified and ready for simulations")
            return True
        else:
            console.print("[red]Error: Missing default data")
            return False
    except Exception as e:
        console.print(f"[red]Verification failed: {e}")
        return False


if __name__ == "__main__":
    console.print("[bold blue]\n=== Simulation Games Database Setup ===")

    # Step 1: Create database
    console.print("\n[bold]1. Checking database...")
    create_database()

    # Step 2: Initialize tables
    console.print("\n[bold]2. Initializing tables...")
    initialize_tables()

    # Step 3: Verify setup
    console.print("\n[bold]3. Verifying setup...")
    if not verify_setup():
        console.print("[red]Setup verification failed!")
        exit(1)

    console.print("\n[bold green]Setup completed successfully! ")