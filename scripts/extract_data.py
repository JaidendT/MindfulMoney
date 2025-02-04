import pandas as pd
import psycopg2

# Define the connection parameters
DB_NAME = "my_expense_tracker"
DB_USER = "postgres"
DB_PASSWORD = "Jaiden14648"
DB_HOST = "localhost"
DB_PORT = "5432"

# Function to connect to the PostgreSQL database
def connect_to_db():
    try:
        # establish connection
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Connected to the database successfully!")
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# Function to insert data into the PostgreSQL database
def insert_data(df, conn):
    try:
        cursor = conn.cursor()

        # Iterate over the DataFrame and insert data into the database
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO transactions (account, posting_date, transaction_date, 
                description, category, money_in, money_out, fee, balance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                row['Account'], row['Posting Date'], row['Transaction Date'], 
                row['Description'], row['Category'], row['Money In'], row['Money Out'], 
                row['Fee'], row['Balance']
            ))
            

        # Commit the transaction and close the connection
        conn.commit()
        print("Data successfully inserted.")
        cursor.close()
    except Exception as e:
        print(f"Error inserting data into the database: {e}")
    
if __name__ == "__main__":
    file_path = "../data/3feb25_12month_statement.txt"
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
