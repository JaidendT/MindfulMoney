# 💰 MindfulMoney - Personal Budgeting Web App

A simple, clean web application for tracking your spending habits by importing bank statement CSV files.

## 🎯 What This App Does

- **Upload CSV files** from your banking app
- **Automatically detect** columns (works with different bank formats)
- **Store transactions** safely in a local SQLite database
- **View all transactions** with color-coded amounts (green = income, red = spending)
- **Analyze spending** with monthly breakdowns and summaries

## 📁 Project Structure

```
MindfulMoney/
├── app.py                 # Main Flask application (web routes & CSV import logic)
├── db.py                  # Database functions (SQLite operations)
├── requirements.txt       # Python package dependencies
├── README.md             # Quick start guide
├── README_DOCS.md        # This file - detailed documentation
├── mindful_money.db      # SQLite database (created automatically)
├── templates/            # HTML templates for web pages
│   ├── base.html         # Base template (navigation, layout)
│   ├── index.html        # Homepage
│   ├── upload.html       # CSV upload page (with drag & drop)
│   ├── transactions.html # Transactions list page
│   └── analytics.html    # Analytics/spending summary page
├── static/               # Static files (CSS, images, JS)
│   └── css/
│       └── style.css     # All styling for the app
├── uploads/              # Temporary storage for uploaded CSV files
└── data/                 # Your bank statements (not uploaded to git)
```

## 🚀 How to Run

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

This installs:
- **Flask** - Web framework for Python
- **pandas** - Data manipulation library for reading/parsing CSV files
- **Werkzeug** - Utilities for Flask (file uploads, security)

### 2. Run the Application
```powershell
python app.py
```

### 3. Open in Browser
Go to: **http://localhost:5000**

## 📊 How the CSV Import Works

### Your Bank's CSV Format
Your CSV files have this structure:
```csv
Nr,Account,Posting Date,Transaction Date,Description,Original Description,Parent Category,Category,Money In,Money Out,Fee,Balance
1,1927752963,2024-11-01,2024-10-30,Grocery Store,...,Food,Food,,-124.00,,1938.32
2,1927752963,2024-11-01,2024-11-01,Payment Received,...,Income,Income,250.00,,,2188.32
```

**Important:** 
- `Money In` = Positive values (income)
- `Money Out` = **Already negative** values (e.g., -124.00 for R124 spent)

### Import Process (in `app.py`)

1. **File Upload** (`/upload` route)
   - User drags & drops or selects CSV file
   - File saved to `uploads/` folder

2. **Column Detection** (`detect_csv_columns()` function)
   - Scans column names (case-insensitive)
   - Maps to standard names: date, description, money_in, money_out, balance, category

3. **Parse Each Row** (loop in `upload()` function)
   - Parse date → converts to YYYY-MM-DD format
   - Parse Money In → keep as positive (income)
   - Parse Money Out → keep as-is (already negative in CSV)
   - Parse balance & category

4. **Duplicate Check** (`transaction_exists()` in `db.py`)
   - Checks if transaction with same date, description, amount exists
   - Skips if duplicate

5. **Save to Database** (`add_transaction()` in `db.py`)
   - Inserts into SQLite database

## 🗄️ Database Schema

The app uses SQLite (a simple file-based database). Here's the table structure:

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each transaction
    date TEXT NOT NULL,                    -- Transaction date (YYYY-MM-DD)
    description TEXT,                      -- Transaction description
    amount REAL NOT NULL,                  -- Amount (positive=income, negative=spending)
    balance REAL,                          -- Account balance after transaction
    category TEXT,                         -- Transaction category from bank
    created_at TEXT DEFAULT CURRENT_TIMESTAMP  -- When added to database
);
```

### Why Positive/Negative Amounts?

- **Positive** (e.g., 250.00) = Money coming **in** (income, payments received)
- **Negative** (e.g., -124.00) = Money going **out** (spending, payments made)

This makes calculations easy:
- Total Income: `SUM(amount) WHERE amount > 0`
- Total Spending: `SUM(amount) WHERE amount < 0`
- Net Balance: `SUM(amount)` (positive + negative = net)

## 🎨 How the Color Coding Works

In `templates/transactions.html` and `analytics.html`:
```html
<td class="{% if transaction.amount < 0 %}amount-negative{% else %}amount-positive{% endif %}">
    R{{ transaction.amount }}
</td>
```

In `static/css/style.css`:
```css
.amount-positive {
    color: #27ae60;              /* Green text */
    background-color: #d5f4e6;   /* Light green background */
}

.amount-negative {
    color: #e74c3c;              /* Red text */
    background-color: #fadbd8;   /* Light red background */
}
```

## 🛠️ Key Files Explained

### `app.py` - Main Application
The heart of the web application. Contains:

- **Flask routes** - URLs that users visit:
  - `/` - Homepage
  - `/upload` - CSV upload page
  - `/transactions` - View all transactions
  - `/analytics` - Spending summaries

- **CSV parsing logic**:
  - `detect_csv_columns()` - Automatically finds the right columns
  - `parse_amount()` - Cleans up currency values
  - `parse_date()` - Handles different date formats

- **File upload handling** - Saves and processes CSV files

### `db.py` - Database Functions
All database operations in one place:

- **`init_db()`** - Creates database and table (safe to call multiple times)
- **`add_transaction()`** - Saves one transaction to database
- **`get_all_transactions()`** - Retrieves all transactions (sorted by date)
- **`transaction_exists()`** - Checks for duplicates before importing
- **`get_spending_summary()`** - Calculates totals and monthly breakdown

### `templates/` - HTML Pages
Uses **Jinja2** templating (Flask's template engine):

- `{{ variable }}` - Displays Python variables in HTML
- `{% if condition %}` - Conditional logic in HTML
- `{% for item in list %}` - Loops in HTML

Structure:
- `base.html` - Master template with navigation (all others extend this)
- `index.html` - Welcome page with feature cards
- `upload.html` - File upload with drag & drop JavaScript
- `transactions.html` - Table of all transactions
- `analytics.html` - Summary cards and monthly breakdown

### `static/css/style.css` - Styling
Modern, clean design with:
- Responsive layout (works on mobile)
- Color-coded amounts
- Hover effects
- Drag & drop visual feedback

## 🐛 Debugging Tips

### Check what's in the database:
```python
from db import get_all_transactions
transactions = get_all_transactions()
for t in transactions[:10]:  # Show first 10
    print(f"{t['date']}: {t['description'][:30]} = R{t['amount']}")
```

### Test CSV column detection:
```python
import pandas as pd
from app import detect_csv_columns

df = pd.read_csv('data/your_file.csv')
mapping = detect_csv_columns(df)
print("Detected columns:", mapping)
```

### Test amount parsing:
```python
from app import parse_amount

print(parse_amount("1,234.56"))  # Should return 1234.56
print(parse_amount("-124.00"))   # Should return -124.0
print(parse_amount("R100"))      # Should return 100.0
```

### Clear database and start fresh:
```powershell
Remove-Item mindful_money.db
python app.py  # Database will be recreated
```

## 🔧 Common Issues & Solutions

### "Money Out transactions not showing as red"
**Cause:** Your CSV's Money Out column already contains negative values  
**Fix:** Line 171-174 in `app.py` now correctly handles this:
```python
elif money_out:
    amount = money_out  # Keep as-is (already negative)
```

### "Can't detect columns"
**Cause:** CSV has unusual column names  
**Fix:** Add your column names to the keyword lists in `detect_csv_columns()`:
```python
date_keywords = ['posting date', 'your custom date name', ...]
```

### "Duplicates keep importing"
**Cause:** Exact match required (date + description + amount)  
**Current behavior:** `transaction_exists()` checks all three fields  
**To modify:** Edit the SQL query in `transaction_exists()` to be more/less strict

### "Drag & drop not working"
**Cause:** JavaScript not loading or browser compatibility  
**Fix:** Check browser console for errors, or use traditional file input button

## 📚 How Flask Works (For Learning)

Flask is a **web framework** that makes it easy to build web applications in Python.

### Routes
Routes map URLs to Python functions:
```python
@app.route('/transactions')
def transactions():
    # This function runs when someone visits /transactions
    data = get_all_transactions()
    return render_template('transactions.html', transactions=data)
```

### Templates
Templates are HTML files with special syntax:
```html
{% for transaction in transactions %}
    <tr>
        <td>{{ transaction.date }}</td>
        <td>{{ transaction.description }}</td>
    </tr>
{% endfor %}
```

### Request Handling
```python
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Form was submitted
        file = request.files['file']
        # Process file...
    else:
        # Just visiting the page
        return render_template('upload.html')
```

## 🎓 Learning Path

If you want to understand and modify this project:

1. **Start with `db.py`**
   - Simple Python functions
   - SQL queries are straightforward
   - Try adding a new function to count transactions

2. **Then `app.py`**
   - Read the comments from top to bottom
   - Understand the route → function → template flow
   - Try adding a new route

3. **Explore Templates**
   - See how Python data becomes HTML
   - Modify the styling in `style.css`
   - Add a new page

4. **Experiment!**
   - Add a search feature
   - Add transaction categories
   - Create charts with a library like Chart.js
   - Filter transactions by date range

## 🤝 Working Together

All code is now **fully documented** with:
- ✅ Detailed comments explaining what each function does
- ✅ Example usage for complex functions
- ✅ Explanations of the logic and why decisions were made
- ✅ This comprehensive README

Feel free to:
- Modify any code
- Add new features
- Ask questions about how anything works
- Experiment and break things (you can always re-upload your CSV!)

## 📝 Next Steps / Ideas

Potential features to add:
- **Search/Filter** - Search transactions by description or category
- **Date Range Filter** - View transactions for specific time periods
- **Charts** - Visual graphs of spending over time
- **Budget Goals** - Set spending limits and track progress
- **Export** - Export filtered transactions to new CSV
- **Categories** - Manual category editing/assignment
- **Tags** - Add custom tags to transactions
- **Recurring Transactions** - Identify and highlight recurring expenses

---

**Built with:** Python 3.13, Flask 3.0, pandas, SQLite  
**Currency:** South African Rand (R)
