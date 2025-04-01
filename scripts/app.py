from flask import Flask, render_template, request, jsonify
import pandas as pd
import psycopg2
from decimal import Decimal
import os
from extract_data import process_csv

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

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

    def format_currency(amount):
        return f"R{amount:,.2f}".replace(",", " ")

    total_income = sum(float(t["money_in"]) for t in transactions if float(t["money_in"]) > 0)
    total_expenses = sum(abs(float(t["money_out"])) for t in transactions if float(t["money_out"]) < 0) + sum(abs(float(t["fee"])) for t in transactions if float(t["fee"]) > 0)
    transactions_sorted = sorted(transactions, key=lambda x: x['transaction_date'], reverse=True)
    final_balance = transactions_sorted[0]["balance"] if transactions_sorted else 0

    return render_template(
        "transactions.html",
        transactions=transactions,
        total_income=format_currency(total_income),
        total_expenses=format_currency(total_expenses),
        balance=format_currency(final_balance)
    )

@app.route("/upload", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save file to the uploads folder
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Process the CSV file and insert data into the database
    success, message = process_csv(file_path)
    
    if success:
        return jsonify({'message': 'CSV uploaded successfully! You can view your data on the Transactions, Income, or Expenses pages.'})
    else:
        return jsonify({'error': message}), 500  # Internal Server Error

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
