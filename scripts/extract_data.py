import pandas as pd
import psycopg2

# Define the connection parameters
DB_NAME = "my_expense_tracker"
DB_USER = "postgres"
DB_PASSWORD = "Jaiden14648"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_to_db():
    """Connect to the PostgreSQL database and return the connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def insert_data(df, conn):
    """Insert transactions data into the PostgreSQL database."""
    try:
        cursor = conn.cursor()

        df = clean_data(df)

        for _, row in df.iterrows():
             # Check if transaction already exists
            cursor.execute("""
                SELECT 1 FROM transactions
                WHERE account = %s AND posting_date = %s 
                AND description = %s 
                AND (money_in = %s OR money_out = %s OR fee = %s);
            """, (
                row['Account'], row['Posting Date'], 
                row['Description'], row['Money In'], 
                row['Money Out'], row['Fee']
            ))

            if not cursor.fetchone():  # If no existing transaction, insert new one
                cursor.execute("""
                    INSERT INTO transactions (account, posting_date, transaction_date, 
                    description, category, money_in, money_out, fee, balance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (
                    row['Account'], row['Posting Date'], row['Transaction Date'], 
                    row['Description'], row['Category'], row['Money In'], 
                    row['Money Out'], row['Fee'], row['Balance']
                ))

        conn.commit()
        cursor.close()
        print("✅ Data inserted successfully.")
    except Exception as e:
        print(f"❌ Error inserting data: {e}")

def process_csv(file_path):
    """Process CSV file and insert data into the database."""
    try:
        df = pd.read_csv(file_path, dtype=str)

        # Convert necessary columns
        df['Money In'] = pd.to_numeric(df['Money In'], errors='coerce').fillna(0)
        df['Money Out'] = pd.to_numeric(df['Money Out'], errors='coerce').fillna(0)
        df['Fee'] = pd.to_numeric(df['Fee'], errors='coerce').fillna(0)
        df['Balance'] = pd.to_numeric(df['Balance'], errors='coerce')

        df['Posting Date'] = pd.to_datetime(df['Posting Date'], errors='coerce')
        df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], errors='coerce')

        conn = connect_to_db()
        if conn:
            insert_data(df, conn)
            conn.close()
            return True, "CSV processed successfully."
        else:
            return False, "Database connection failed."
    except Exception as e:
        return False, f"❌ Error processing CSV: {e}"


def clean_data(df):
    # Fill blank 'Money In' with 0.00
    df['Money In'] = df['Money In'].fillna(0).astype(float)
    df['Money Out'] = df['Money Out'].fillna(0).astype(float)
    df['Fee'] = df['Fee'].fillna(0).astype(float)

    # Drop rows where both 'Money In' and 'Money Out' are NaN
    df = df[(df['Money In'] != 0) | (df['Money Out'] != 0) | (df['Fee'] != 0)]

    # Remove duplicate transactions (same account, date, description, category, money in, money out, and fee)
    df = df.drop_duplicates(subset=['Account', 'Posting Date', 'Description', 'Category', 'Money In', 'Money Out', 'Fee'])

    # Remove rows where 'Balance' is NaN
    df = df.dropna(subset=['Balance'])

    return df
