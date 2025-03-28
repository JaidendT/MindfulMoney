from flask import Flask, render_template, request
import psycopg2
import os

app = Flask(__name__)

# Connect to PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        dbname="my_expense_tracker",
        user="postgres",
        password="Jaiden14648",
        host="localhost",
        port="5432"
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

    # Print to check if data is being fetched
    print(f"Fetched {len(transactions)} transactions")

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

    # Function to format currency with 'R' and spaces after every 3 digits
    def format_currency(amount):
        return f"R{amount:,.2f}".replace(",", " ")

    # Sum logic using float for correct type handling
    total_income = sum(float(t["money_in"]) for t in transactions if float(t["money_in"]) > 0)
    total_expenses = sum(abs(float(t["money_out"])) for t in transactions if float(t["money_out"]) < 0) + sum(abs(float(t["fee"])) for t in transactions if float(t["fee"]) > 0)
    transactions_sorted = sorted(transactions, key=lambda x: x['transaction_date'], reverse=True)
    final_balance = transactions_sorted[0]["balance"] if transactions_sorted else 0

    # Format totals and balance
    formatted_total_income = format_currency(total_income)
    formatted_total_expenses = format_currency(total_expenses)
    formatted_balance = format_currency(final_balance)

    return render_template("transactions.html", transactions=transactions, 
        total_income=formatted_total_income, 
        total_expenses=formatted_total_expenses,
        balance=formatted_balance)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)