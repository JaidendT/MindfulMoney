from flask import Flask, render_template, request
import psycopg2
import os

app = Flask(__name__)

# Connect to PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        dbname="your_db_name",
        user="your_db_user",
        password="your_db_password",
        host="your_db_host",
        port="your_db_port"
    )

@app.route("/transactions")
def transactions():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get date filters from request parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Query with optional date filtering
    if start_date and end_date:
        cur.execute("""
            SELECT account, posting_date, transaction_date, description, category, money_in, money_out, fee, balance 
            FROM transactions
            WHERE transaction_date BETWEEN %s AND %s
            ORDER BY transaction_date DESC
        """, (start_date, end_date))
    else:
        cur.execute("SELECT account, posting_date, transaction_date, description, category, money_in, money_out, fee, balance FROM transactions ORDER BY transaction_date DESC")

    transactions = cur.fetchall()
    cur.close()
    conn.close()

    # Convert tuple data to dictionaries for Jinja
    transactions = [
        {
            "account": row[0],
            "posting_date": row[1],
            "transaction_date": row[2],
            "description": row[3],
            "category": row[4],
            "money_in": row[5],
            "money_out": row[6],
            "fee": row[7],
            "balance": row[8],
        }
        for row in transactions
    ]

    return render_template("transactions.html", transactions=transactions)

if __name__ == "__main__":
    app.run(debug=True)

