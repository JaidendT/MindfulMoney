from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        dbname="my_expense_tracker",
        user="postgres",
        password="Jaiden14648",
        host="localhost",
        port="5432"
    )
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM transactions ORDER BY transaction_date DESC")
    transactions = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)