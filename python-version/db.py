"""
Database Module for MindfulMoney
=================================

This module handles all database operations for storing and retrieving transactions.

Database Structure:
    - Uses SQLite (a simple file-based database)
    - Database file: mindful_money.db (created in project root)
    - Single table: transactions
    
Transaction Table Schema:
    - id: Auto-incrementing primary key
    - date: Transaction date (TEXT in YYYY-MM-DD format)
    - description: Transaction description/memo
    - amount: Transaction amount (REAL number)
        * Positive values = money coming in (income)
        * Negative values = money going out (spending)
    - balance: Account balance after transaction (optional)
    - category: Transaction category (optional, from bank CSV)
    - created_at: Timestamp when record was added to database
"""

import sqlite3
from datetime import datetime
from contextlib import contextmanager

# Path to the SQLite database file
DATABASE_PATH = "mindful_money.db"


def init_db():
    """
    Initialize the database and create tables if they don't exist.
    
    This function is called when the app starts. If the database file
    doesn't exist, it creates it. If the transactions table doesn't exist,
    it creates that too.
    
    This is safe to call multiple times - it won't delete existing data.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create the transactions table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL,
            balance REAL,
            category TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


@contextmanager
def get_db():
    """
    Context manager for database connections.
    
    This is a Python context manager (used with 'with' statement) that:
    1. Opens a database connection
    2. Sets it to return rows as dictionaries (easier to work with)
    3. Automatically closes the connection when done
    
    Usage:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions")
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries instead of tuples
    try:
        yield conn
    finally:
        conn.close()


def add_transaction(date, description, amount, balance=None, category=None):
    """
    Add a single transaction to the database.
    
    Args:
        date (str): Transaction date in YYYY-MM-DD format
        description (str): Transaction description/memo
        amount (float): Transaction amount
            - Positive for income (money in)
            - Negative for spending (money out)
        balance (float, optional): Account balance after transaction
        category (str, optional): Transaction category
    
    Returns:
        int: The ID of the newly inserted transaction
    
    Example:
        add_transaction('2024-11-26', 'Grocery Store', -150.50, 2000.00, 'Food')
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (date, description, amount, balance, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, description, amount, balance, category))
        conn.commit()
        return cursor.lastrowid


def get_all_transactions():
    """
    Get all transactions from the database, ordered by date (newest first).
    
    Returns:
        list: List of dictionaries, each containing:
            - id: Transaction ID
            - date: Transaction date
            - description: Transaction description
            - amount: Transaction amount (positive=income, negative=spending)
            - balance: Account balance (if available)
            - category: Transaction category (if available)
    
    Example:
        transactions = get_all_transactions()
        for t in transactions:
            print(f"{t['date']}: {t['description']} - R{t['amount']}")
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, date, description, amount, balance, category
            FROM transactions
            ORDER BY date DESC
        ''')
        return [dict(row) for row in cursor.fetchall()]


def transaction_exists(date, description, amount):
    """
    Check if a transaction already exists in the database.
    
    This is used to prevent duplicate imports when uploading the same
    CSV file multiple times.
    
    Args:
        date (str): Transaction date
        description (str): Transaction description
        amount (float): Transaction amount
    
    Returns:
        bool: True if transaction exists, False otherwise
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM transactions
            WHERE date = ? AND description = ? AND amount = ?
        ''', (date, description, amount))
        return cursor.fetchone() is not None


def get_spending_summary():
    """
    Calculate spending summary and statistics.
    
    This function analyzes all transactions in the database and returns:
    - Total income (sum of all positive amounts)
    - Total spending (sum of all negative amounts, returned as positive)
    - Net balance (income - spending)
    - Monthly breakdown of income and spending
    
    Returns:
        dict: Dictionary containing:
            - total_income: Total money received
            - total_spending: Total money spent (as positive number)
            - net: Net balance (total_income - total_spending)
            - monthly: List of monthly summaries, each with:
                * month: Month in YYYY-MM format
                * income: Income for that month
                * spending: Spending for that month (as negative number)
    
    Example:
        summary = get_spending_summary()
        print(f"Total Income: R{summary['total_income']}")
        print(f"Total Spending: R{summary['total_spending']}")
        print(f"Net: R{summary['net']}")
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total income (positive amounts only)
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE amount > 0')
        total_income = cursor.fetchone()[0] or 0
        
        # Total spending (negative amounts only)
        cursor.execute('SELECT SUM(amount) FROM transactions WHERE amount < 0')
        total_spending = cursor.fetchone()[0] or 0
        
        # Monthly breakdown using SQL to group by month
        cursor.execute('''
            SELECT strftime('%Y-%m', date) as month, 
                   SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN amount < 0 THEN amount ELSE 0 END) as spending
            FROM transactions
            GROUP BY month
            ORDER BY month DESC
        ''')
        monthly = [dict(row) for row in cursor.fetchall()]
        
        return {
            'total_income': total_income,
            'total_spending': abs(total_spending),  # Convert to positive for display
            'net': total_income + total_spending,    # total_spending is already negative
            'monthly': monthly
        }
