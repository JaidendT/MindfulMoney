from flask import Flask, render_template, request, jsonify
import pandas as pd
import psycopg2
from decimal import Decimal, InvalidOperation
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

def safe_decimal(value):
    try:
        # Ensure that `value` is properly converted to Decimal, defaulting to Decimal('0.00')
        return Decimal(str(value)) if value is not None else Decimal('0.00')
    except (InvalidOperation, TypeError, ValueError):
        return Decimal('0.00')  # Return a safe 0.00 if anything goes wrong

@app.route("/transactions")
def transactions():
    conn = get_db_connection()
    cur = conn.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Query for transactions
    if start_date and end_date:
        cur.execute(""" 
            SELECT nr, transaction_date, description, category, 
                money_in, money_out, fee, balance
            FROM transactions
            WHERE transaction_date BETWEEN %s AND %s
            ORDER BY transaction_date DESC;
        """, (start_date, end_date))
    else:
        cur.execute("""
            SELECT nr, transaction_date, description, category, 
                money_in, money_out, fee, balance
            FROM transactions
            ORDER BY transaction_date DESC;
        """)

    transactions = cur.fetchall()

    # Query for total income and total expenses
    if start_date and end_date:
        cur.execute("""
            SELECT 
                SUM(CASE WHEN money_in IS NOT NULL AND money_in > 0 THEN money_in ELSE 0 END) AS total_income,
                SUM(CASE WHEN money_out IS NOT NULL THEN ABS(money_out) ELSE 0 END) + 
                SUM(CASE WHEN fee IS NOT NULL THEN ABS(fee) ELSE 0 END) AS total_expenses
            FROM transactions
            WHERE transaction_date BETWEEN %s AND %s;
        """, (start_date, end_date))
    else:
        cur.execute("""
            SELECT 
                SUM(CASE WHEN money_in IS NOT NULL AND money_in > 0 THEN money_in ELSE 0 END) AS total_income,
                SUM(CASE WHEN money_out IS NOT NULL THEN ABS(money_out) ELSE 0 END) + 
                SUM(CASE WHEN fee IS NOT NULL THEN ABS(fee) ELSE 0 END) AS total_expenses
            FROM transactions;
        """)

    # Fetch totals
    totals = cur.fetchone()

    if totals:
        # Handle the case where we might still get NaN from the database
        total_income = totals[0]
        total_expenses = totals[1]
        
        # Check for NaN and replace with 0.00
        if total_income != total_income or str(total_income) == 'NaN':
            total_income = Decimal('0.00')
        if total_expenses != total_expenses or str(total_expenses) == 'NaN':
            total_expenses = Decimal('0.00')
    else:
        total_income, total_expenses = Decimal('0.00'), Decimal('0.00')
    
    # Fetch distinct categories
    cur.execute("SELECT DISTINCT category FROM transactions")
    categories = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    transactions = [
        {
            "nr": row[0],
            "transaction_date": row[1],
            "description": row[2],
            "category": row[3],
            "money_in": row[4],
            "money_out": row[5],
            "fee": row[6],
            "balance": row[7]
        }
        for row in transactions
    ]

    def format_currency(amount):
        try:
            # Convert to string first then to Decimal to handle various input types
            amount_decimal = Decimal(str(amount)) if amount is not None else Decimal('0.00')
            return f"R{amount_decimal:,.2f}".replace(",", " ")
        except (InvalidOperation, TypeError, ValueError) as e:
            return "R0.00"
       
    transactions_sorted = sorted(transactions, key=lambda x: x['transaction_date'], reverse=True)
    final_balance = transactions_sorted[0]["balance"] if transactions_sorted else 0

    return render_template(
        "transactions.html",
        transactions=transactions,
        categories=categories,
        total_income=format_currency(total_income),
        total_expenses=format_currency(total_expenses),
        balance=format_currency(final_balance)
    )

@app.route("/upload", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded.'}), 400  # Unified key: message
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file.'}), 400  # Unified key: message

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    success, message = process_csv(file_path)

    if success:
        return jsonify({'message': 'CSV uploaded successfully! You can view your data on the Transactions, Income, or Expenses pages.'}), 200
    else:
        return jsonify({'message': message}), 500  # Unified key: message
    

@app.route("/update-transactions", methods=["POST"])
def update_transactions():
    data = request.get_json()
    print("Received data:", data)

    if not data or not isinstance(data, list):
        return jsonify({"error": "Invalid data format"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for transaction in data:
            nr = transaction.get("nr")
            category = transaction.get("category")

            if nr is None:
                continue  # skip if nr is missing

            cur.execute("""
                UPDATE transactions
                SET category = %s
                WHERE nr = %s
            """, (category, nr))
        
        conn.commit()
        return jsonify({"success": True, "message": "Changes saved successfully!"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
