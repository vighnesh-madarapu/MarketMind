
import sqlite3
from config import Config

# Use database path from config.py
DATABASE = Config.DATABASE_PATH


def get_db_connection():
    """
    Create and return a SQLite database connection.
    """

    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        DATABASE,
        timeout=30
    )

    connection.row_factory = sqlite3.Row

    # Enable foreign key validation
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():
    """
    Initialize all MarketMind database tables.
    Existing records are preserved.
    """

    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    connection = get_db_connection()

    try:
        connection.executescript("""

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            campaign_name TEXT NOT NULL,
            platform TEXT NOT NULL,
            budget REAL DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            clicks INTEGER DEFAULT 0,
            conversions INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            email TEXT,
            age INTEGER,
            location TEXT,
            purchase_amount REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            competitor_name TEXT NOT NULL,
            platform TEXT,
            followers INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS content_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            platform TEXT,
            post_date TEXT,
            status TEXT DEFAULT 'Planned',
            FOREIGN KEY(user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
                ON DELETE CASCADE
        );

        """)

        # Improve query performance
        connection.executescript("""
        CREATE INDEX IF NOT EXISTS idx_campaigns_user
        ON campaigns(user_id);

        CREATE INDEX IF NOT EXISTS idx_customers_user
        ON customers(user_id);

        CREATE INDEX IF NOT EXISTS idx_competitors_user
        ON competitors(user_id);

        CREATE INDEX IF NOT EXISTS idx_content_posts_user
        ON content_posts(user_id);

        CREATE INDEX IF NOT EXISTS idx_activity_logs_user
        ON activity_logs(user_id);
        """)

        connection.commit()

        print("MarketMind database initialized successfully!")

    except sqlite3.Error as error:
        connection.rollback()
        print(f"Database initialization error: {error}")
        raise

    finally:
        connection.close()
