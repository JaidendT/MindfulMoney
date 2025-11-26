"""
MindfulMoney - Personal Budgeting Web Application
==================================================

This is the main Flask application file that handles:
- Web page routes (URLs)
- CSV file uploads
- Transaction imports
- Data display and analytics

How Flask works:
    Flask is a web framework that maps URLs to Python functions.
    When someone visits a URL (e.g., /upload), Flask calls the
    corresponding function and returns HTML to display.

Routes in this app:
    / (index)           - Homepage
    /upload            - Upload CSV files
    /transactions      - View all transactions
    /analytics         - View spending summaries
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from db import init_db, add_transaction, get_all_transactions, transaction_exists, get_spending_summary

# Create the Flask app instance
app = Flask(__name__)

# Secret key for session management (used for flash messages)
# In production, this should be a random string stored securely
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'  # Folder where uploaded CSV files are temporarily stored
ALLOWED_EXTENSIONS = {'csv'}  # Only allow CSV files

# Create the uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the database (creates tables if they don't exist)
init_db()


def allowed_file(filename):
    """
    Check if the uploaded file has a valid extension.
    
    Args:
        filename (str): Name of the uploaded file
    
    Returns:
        bool: True if file extension is .csv, False otherwise
    
    Example:
        allowed_file('statement.csv')  # Returns True
        allowed_file('statement.xlsx') # Returns False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def detect_csv_columns(df):
    """
    Automatically detect which columns in the CSV contain transaction data.
    
    Different banks use different column names in their CSV exports.
    This function tries to find the right columns by looking for common
    keywords in the column names.
    
    Args:
        df (pandas.DataFrame): The CSV data loaded into a pandas DataFrame
    
    Returns:
        dict: A dictionary mapping standard names to actual column names:
            - 'date': The column containing transaction dates
            - 'description': The column containing transaction descriptions
            - 'money_in': Column for incoming money (if separate columns)
            - 'money_out': Column for outgoing money (if separate columns)
            - 'amount': Single column for amounts (if not separate)
            - 'balance': Account balance column (optional)
            - 'category': Transaction category column (optional)
    
    Example:
        If CSV has columns: ['Posting Date', 'Description', 'Money In', 'Money Out']
        Returns: {
            'date': 'Posting Date',
            'description': 'Description',
            'money_in': 'Money In',
            'money_out': 'Money Out'
        }
    """
    # Create a lowercase mapping of all column names for case-insensitive matching
    columns = {col.lower().strip(): col for col in df.columns}
    
    mapping = {}
    
    # Find date column (prefer Posting Date over Transaction Date)
    # We try multiple common names for date columns
    date_keywords = ['posting date', 'transaction date', 'date', 'trans date']
    for keyword in date_keywords:
        if keyword in columns:
            mapping['date'] = columns[keyword]
            break
    
    # Find description column
    desc_keywords = ['description', 'original description', 'details', 'memo', 'narrative', 'particulars']
    for keyword in desc_keywords:
        if keyword in columns:
            mapping['description'] = columns[keyword]
            break
    
    # Check if we have Money In/Money Out columns (standard banking format)
    # Some banks separate income and expenses into different columns
    if 'money in' in columns and 'money out' in columns:
        mapping['money_in'] = columns['money in']
        mapping['money_out'] = columns['money out']
    else:
        # Find single amount column (some banks use one column for both)
        amount_keywords = ['amount', 'value', 'debit', 'credit', 'transaction amount']
        for keyword in amount_keywords:
            if keyword in columns:
                mapping['amount'] = columns[keyword]
                break
    
    # Find balance column (optional - shows account balance after transaction)
    balance_keywords = ['balance', 'running balance', 'account balance']
    for keyword in balance_keywords:
        if keyword in columns:
            mapping['balance'] = columns[keyword]
            break
    
    # Find category column (optional - transaction category from bank)
    category_keywords = ['category', 'parent category']
    for keyword in category_keywords:
        if keyword in columns:
            mapping['category'] = columns[keyword]
            break
    
    return mapping


def parse_amount(value):
    """
    Parse and clean amount values from CSV files.
    
    CSV files can have amounts in different formats:
    - With commas: 1,234.56
    - With currency symbols: $50.00 or R50.00
    - In accounting format (parentheses for negative): (50.00)
    - Already negative: -50.00
    - Empty cells (NaN)
    
    Args:
        value: The amount value from the CSV (could be string, number, or NaN)
    
    Returns:
        float: The cleaned numeric value, or None if invalid
    
    Examples:
        parse_amount("1,234.56")  # Returns 1234.56
        parse_amount("(50.00)")   # Returns -50.0
        parse_amount("R100")      # Returns 100.0
        parse_amount(NaN)         # Returns None
    """
    # Check if value is empty (NaN = Not a Number in pandas)
    if pd.isna(value):
        return None
    
    # Convert to string and clean common formatting
    value_str = str(value).strip().replace(',', '').replace('$', '').replace('R', '')
    
    # Handle parentheses as negative (accounting format)
    # Example: (50.00) means -50.00
    if value_str.startswith('(') and value_str.endswith(')'):
        value_str = '-' + value_str[1:-1]
    
    try:
        return float(value_str)
    except ValueError:
        # If conversion fails, return None
        return None


def parse_date(value):
    """
    Parse date values from CSV files into standard format.
    
    Different banks export dates in different formats:
    - DD/MM/YYYY (e.g., 31/12/2024)
    - MM/DD/YYYY (e.g., 12/31/2024)
    - YYYY-MM-DD (e.g., 2024-12-31)
    - DD-MM-YYYY (e.g., 31-12-2024)
    
    This function tries multiple formats until one works.
    
    Args:
        value: The date value from CSV (string or datetime)
    
    Returns:
        str: Date in YYYY-MM-DD format (standard SQL format), or None if invalid
    
    Examples:
        parse_date("31/12/2024")   # Returns "2024-12-31"
        parse_date("2024-12-31")   # Returns "2024-12-31"
        parse_date(NaN)            # Returns None
    """
    if pd.isna(value):
        return None
    
    # Try pandas datetime parser first (it's smart and handles many formats)
    try:
        return pd.to_datetime(value).strftime('%Y-%m-%d')
    except:
        pass
    
    # If pandas fails, try common date formats manually
    formats = ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(str(value), fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    # If all formats fail, return None
    return None


@app.route('/')
def index():
    """
    Homepage route - displays the welcome page.
    
    When someone visits http://localhost:5000/, Flask calls this function
    and returns the index.html template.
    """
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    CSV Upload route - handles file uploads and imports transactions.
    
    This route handles two different HTTP methods:
    - GET:  Someone visits /upload - show the upload form
    - POST: Someone submits the form - process the uploaded file
    
    Process:
    1. Validate the uploaded file exists and is a CSV
    2. Save the file temporarily
    3. Read and parse the CSV using pandas
    4. Detect which columns contain date, description, amounts
    5. Loop through each row and import valid transactions
    6. Redirect to transactions page to show imported data
    """
    if request.method == 'POST':
        # POST request = form was submitted with a file
        
        # Check if a file was included in the request
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if user actually selected a file
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Check if file is a CSV
        if file and allowed_file(file.filename):
            # Secure the filename to prevent malicious file names
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            try:
                # Read CSV file using pandas (powerful data library)
                df = pd.read_csv(filepath)
                
                # Detect which columns contain our needed data
                col_mapping = detect_csv_columns(df)
                
                # Validate we found the required columns
                if 'date' not in col_mapping:
                    flash('Could not detect date column. Please check your CSV file.', 'error')
                    return redirect(request.url)
                
                # We need either Money In/Out columns OR a single Amount column
                if 'money_in' not in col_mapping and 'money_out' not in col_mapping and 'amount' not in col_mapping:
                    flash('Could not detect amount columns. Please check your CSV file.', 'error')
                    return redirect(request.url)
                
                # Import transactions from CSV
                imported = 0  # Count of successfully imported transactions
                skipped = 0   # Count of skipped transactions (duplicates or invalid)
                
                # Loop through each row in the CSV
                for _, row in df.iterrows():
                    # Parse the date
                    date = parse_date(row[col_mapping['date']])
                    if not date:
                        skipped += 1
                        continue  # Skip this row if date is invalid
                    
                    # Handle Money In/Money Out format (YOUR BANK'S FORMAT)
                    # IMPORTANT: Your bank already uses negative numbers for Money Out
                    # Example: Money Out = -124.00 means R124 was spent
                    if 'money_in' in col_mapping and 'money_out' in col_mapping:
                        money_in = parse_amount(row[col_mapping['money_in']])
                        money_out = parse_amount(row[col_mapping['money_out']])
                        
                        # Determine the final amount for this transaction
                        # Money In = positive (income)
                        # Money Out = already negative in your CSV, so keep as-is
                        if money_in and money_in > 0:
                            amount = money_in  # Keep positive for income
                        elif money_out:
                            # YOUR FIX: Money Out is already negative, don't negate it again!
                            amount = money_out  # Keep as-is (already negative)
                        else:
                            # Both columns are empty or zero - skip this row
                            skipped += 1
                            continue
                    else:
                        # Handle single amount column format (other banks)
                        amount = parse_amount(row[col_mapping['amount']])
                        if amount is None:
                            skipped += 1
                            continue
                    
                    # Get optional fields
                    description = str(row[col_mapping.get('description', '')]) if 'description' in col_mapping else ''
                    balance = parse_amount(row[col_mapping['balance']]) if 'balance' in col_mapping else None
                    category = str(row[col_mapping['category']]) if 'category' in col_mapping else None
                    
                    # Check for duplicates to avoid importing the same transaction twice
                    if transaction_exists(date, description, amount):
                        skipped += 1
                        continue
                    
                    # Add transaction to database
                    add_transaction(date, description, amount, balance, category)
                    imported += 1
                
                # Show success message and redirect to transactions page
                flash(f'Successfully imported {imported} transactions. Skipped {skipped} duplicates or invalid rows.', 'success')
                return redirect(url_for('transactions'))
                
            except Exception as e:
                # If anything goes wrong, show an error message
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a CSV file.', 'error')
            return redirect(request.url)
    
    # GET request - just show the upload form
    return render_template('upload.html')


@app.route('/transactions')
def transactions():
    """
    Transactions list route - displays all imported transactions.
    
    This route:
    1. Gets all transactions from the database
    2. Passes them to the template for display
    3. The template will show them in a table with color coding
       (green for income, red for spending)
    """
    all_transactions = get_all_transactions()
    return render_template('transactions.html', transactions=all_transactions)


@app.route('/analytics')
def analytics():
    """
    Analytics route - displays spending summaries and insights.
    
    This route:
    1. Gets spending summary from database (totals and monthly breakdown)
    2. Passes it to the template
    3. Template displays:
       - Total income
       - Total spending
       - Net balance
       - Monthly breakdown table
    """
    summary = get_spending_summary()
    return render_template('analytics.html', summary=summary)


if __name__ == '__main__':
    # Run the Flask development server
    # debug=True means:
    # - Auto-reload when code changes
    # - Show detailed error messages
    # - Enable debugger
    # WARNING: Never use debug=True in production!
    app.run(debug=True)
