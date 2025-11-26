# 💰 MindfulMoney

A personal budgeting web app for tracking spending habits by importing bank CSV files.

## Quick Start

```powershell
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open browser to http://localhost:5000
```

## What It Does

✅ Upload bank CSV files (drag & drop supported)  
✅ Auto-detect CSV columns  
✅ Store transactions in SQLite database  
✅ View transactions with color coding (green = income, red = spending)  
✅ Monthly spending analytics  

## Project Structure

- `app.py` - Main Flask application (fully documented)
- `db.py` - Database operations (fully documented)
- `templates/` - HTML pages
- `static/css/` - Styling
- `mindful_money.db` - SQLite database (created automatically)

## Documentation

📖 See **[README_DOCS.md](README_DOCS.md)** for:
- Detailed code explanations
- How CSV import works
- Database schema
- Debugging tips
- Learning guide
- Ideas for new features

All code is **fully commented** to help you understand and modify it!

## Your Bank CSV Format

The app handles your bank's format with:
- `Posting Date` → Transaction date
- `Description` → Transaction details
- `Money In` → Income (positive values)
- `Money Out` → Spending (negative values, e.g., -124.00)
- `Category` → Transaction category
- `Balance` → Account balance

## Tech Stack

- Python 3.13
- Flask 3.0 (Web framework)
- pandas (CSV parsing)
- SQLite (Database)
- HTML/CSS/JavaScript

## Features

- 📤 Drag & drop file upload
- 🎨 Color-coded amounts (green/red)
- 💾 Duplicate detection
- 📊 Monthly breakdown
- 🔍 Auto column detection
- 💰 South African Rand (R) currency

## Clear Database & Restart

```powershell
Remove-Item mindful_money.db
python app.py
```

---

**Made for learning and collaboration** - All code documented!
