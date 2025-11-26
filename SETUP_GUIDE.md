# MindfulMoney Modernization - Setup Guide

## ✅ What I've Created

### 1. Backend (Express.js + Prisma + PostgreSQL) - COMPLETE
Location: `backend/`

**Files created:**
- `package.json` - Dependencies and scripts
- `src/server.js` - Main Express server
- `src/routes/transactions.js` - Transaction CRUD API
- `src/routes/upload.js` - CSV upload endpoint
- `src/routes/analytics.js` - Analytics endpoints  
- `prisma/schema.prisma` - Database schema
- `.env.example` - Environment template
- `README.md` - Complete backend documentation

**Security:** All routes use Prisma ORM which automatically prevents SQL injection through parameterized queries.

### 2. Project Organization - COMPLETE
- Moved Python version to `python-version/`
- Created `backend/` for Express.js
- Created `frontend/` for React (setup next)

## 🚀 Next Steps for You

### Step 1: Install PostgreSQL (if not already installed)
Download from: https://www.postgresql.org/download/windows/

During installation:
- Set a password for the `postgres` user (remember this!)
- Default port 5432 is fine

### Step 2: Set Up Backend

```powershell
# Navigate to backend
cd backend

# Install Node.js dependencies
npm install

# Create .env file
copy .env.example .env

# Edit .env file and update DATABASE_URL:
# Replace 'password' with your actual PostgreSQL password
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/mindful_money?schema=public"
```

### Step 3: Create Database

```powershell
# Open PostgreSQL command line
psql -U postgres

# Create database
CREATE DATABASE mindful_money;

# Exit psql
\q
```

### Step 4: Initialize Prisma

```powershell
# Still in backend/ directory

# Generate Prisma Client
npm run db:generate

# Create database tables
npm run db:push
```

### Step 5: Start Backend

```powershell
npm run dev
```

You should see:
```
🚀 Server running on http://localhost:5000
📊 API endpoints available at http://localhost:5000/api
```

### Step 6: Test the API

In a new PowerShell window:

```powershell
# Test health check
Invoke-RestMethod -Uri http://localhost:5000/api/health

# Get all transactions (should be empty initially)
Invoke-RestMethod -Uri http://localhost:5000/api/transactions
```

## 📋 What's Next (After Backend Works)

Once your backend is running successfully, we'll create the React frontend. The frontend will:

1. **Modern UI Components:**
   - Dashboard with statistics
   - Transaction list with filtering
   - CSV upload with drag & drop
   - Analytics charts

2. **React Features:**
   - Component-based architecture
   - React Router for navigation
   - Axios for API calls
   - State management with hooks

3. **Styling:**
   - Modern CSS or Tailwind CSS
   - Responsive design
   - Color-coded transactions

## 🔍 Understanding the Backend

### API Endpoints Created

**Transactions:**
- `GET /api/transactions` - Get all transactions
- `GET /api/transactions/:id` - Get one transaction
- `POST /api/transactions` - Create transaction
- `PUT /api/transactions/:id` - Update transaction
- `DELETE /api/transactions/:id` - Delete transaction

**Upload:**
- `POST /api/upload` - Upload CSV file

**Analytics:**
- `GET /api/analytics/summary` - Financial summary
- `GET /api/analytics/categories` - Category breakdown

### How Prisma Prevents SQL Injection

**Safe (what we use):**
```javascript
await prisma.transaction.create({
  data: {
    description: userInput,  // Prisma automatically parameterizes
    amount: userAmount
  }
});
```

**Unsafe (what NOT to do):**
```javascript
// NEVER concatenate user input into SQL:
`INSERT INTO transactions VALUES ('${userInput}')`
```

Prisma internally converts your queries to parameterized statements, making SQL injection impossible.

## 🐛 Troubleshooting

### "npm: command not found"
- Install Node.js from https://nodejs.org/
- Restart PowerShell after installation

### "psql: command not found"  
- Add PostgreSQL to PATH
- Or use pgAdmin GUI instead

### "Connection refused" or database errors
- Ensure PostgreSQL service is running
- Check DATABASE_URL in `.env` is correct
- Verify database was created

### Port 5000 already in use
- Change PORT in `.env` to 5001 or another port
- Or stop the process using port 5000

## 📚 Learning Resources

- **Express.js:** https://expressjs.com/en/starter/hello-world.html
- **Prisma:** https://www.prisma.io/docs/getting-started
- **PostgreSQL:** https://www.postgresqltutorial.com/

## ✅ Checklist

- [ ] PostgreSQL installed
- [ ] Node.js installed
- [ ] Backend dependencies installed (`npm install`)
- [ ] `.env` file created and configured
- [ ] Database created (`CREATE DATABASE mindful_money`)
- [ ] Prisma initialized (`npm run db:generate` + `npm run db:push`)
- [ ] Backend server running (`npm run dev`)
- [ ] API tested (health check works)

Once all checkboxes are complete, let me know and we'll build the React frontend together!

---

**Questions?** Read `backend/README.md` for detailed explanations of each component.
