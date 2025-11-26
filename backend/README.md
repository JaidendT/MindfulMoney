# MindfulMoney Backend - Express.js + Prisma + PostgreSQL

Modern REST API backend for the MindfulMoney budgeting application.

## 🛠️ Tech Stack

- **Express.js** - Fast, minimalist web framework
- **Prisma ORM** - Type-safe database access (prevents SQL injection)
- **PostgreSQL** - Robust, production-ready database
- **Node.js** - JavaScript runtime

## 📋 Prerequisites

Before you start, make sure you have installed:
- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **PostgreSQL** (v14 or higher) - [Download](https://www.postgresql.org/download/)

## 🚀 Getting Started

### 1. Install Dependencies

```powershell
cd backend
npm install
```

### 2. Set Up PostgreSQL Database

**Option A: Using pgAdmin or psql**
```sql
CREATE DATABASE mindful_money;
```

**Option B: Using PowerShell**
```powershell
psql -U postgres
CREATE DATABASE mindful_money;
\q
```

### 3. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL="postgresql://postgres:your_password@localhost:5432/mindful_money?schema=public"
PORT=5000
CORS_ORIGIN=http://localhost:3000
```

Replace `your_password` with your PostgreSQL password.

### 4. Initialize Database with Prisma

```powershell
# Generate Prisma Client
npm run db:generate

# Push schema to database (creates tables)
npm run db:push
```

### 5. Start the Server

```powershell
# Development mode (auto-restart on changes)
npm run dev

# Production mode
npm start
```

The API will be available at **http://localhost:5000**

## 📚 API Endpoints

### Health Check
```
GET /api/health
```

### Transactions
```
GET    /api/transactions           # Get all transactions
GET    /api/transactions/:id       # Get single transaction
POST   /api/transactions           # Create transaction
PUT    /api/transactions/:id       # Update transaction
DELETE /api/transactions/:id       # Delete transaction
```

### Upload
```
POST   /api/upload                 # Upload CSV file
```

### Analytics
```
GET    /api/analytics/summary      # Get financial summary
GET    /api/analytics/categories   # Get spending by category
```

## 🔒 Security Features

### SQL Injection Prevention

Prisma automatically uses parameterized queries. This code:

```javascript
await prisma.transaction.create({
  data: {
    description: userInput,  // Safe - Prisma handles this
    amount: userAmount
  }
});
```

Is internally converted to a parameterized query, preventing SQL injection.

### What NOT to do (unsafe):
```javascript
// NEVER do raw string concatenation:
await prisma.$executeRawUnsafe(
  `INSERT INTO transactions (description) VALUES ('${userInput}')`
);
```

### Safe raw queries (if needed):
```javascript
// Use tagged templates for safety:
await prisma.$queryRaw`
  SELECT * FROM transactions WHERE date > ${dateValue}
`;
```

## 📁 Project Structure

```
backend/
├── src/
│   ├── server.js           # Main Express server
│   └── routes/
│       ├── transactions.js # Transaction CRUD endpoints
│       ├── upload.js       # CSV upload handling
│       └── analytics.js    # Analytics endpoints
├── prisma/
│   └── schema.prisma       # Database schema definition
├── uploads/                # Temporary CSV storage
├── .env                    # Environment variables (create this)
├── .env.example            # Example environment file
├── package.json            # Dependencies and scripts
└── README.md              # This file
```

## 🗄️ Database Schema

```prisma
model Transaction {
  id          Int      @id @default(autoincrement())
  date        DateTime
  description String?
  amount      Float    // Positive = income, Negative = spending
  balance     Float?
  category    String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}
```

## 🧪 Testing the API

### Using PowerShell (Invoke-RestMethod)

```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:5000/api/health

# Get all transactions
Invoke-RestMethod -Uri http://localhost:5000/api/transactions

# Create a transaction
$body = @{
    date = "2024-11-26"
    description = "Test Transaction"
    amount = -50.00
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:5000/api/transactions -Method Post -Body $body -ContentType "application/json"

# Get analytics summary
Invoke-RestMethod -Uri http://localhost:5000/api/analytics/summary
```

### Using curl (if installed)

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/transactions
```

## 🔧 Useful Commands

```powershell
# View database in browser
npm run db:studio

# Reset database (careful - deletes all data!)
npx prisma db push --force-reset

# View Prisma schema in VS Code with syntax highlighting
# Install: Prisma extension in VS Code
```

## 🐛 Troubleshooting

### "Can't connect to database"
- Check PostgreSQL is running: `Get-Service postgresql*`
- Verify DATABASE_URL in `.env` is correct
- Test connection: `psql -U postgres -d mindful_money`

### "Port 5000 already in use"
- Change PORT in `.env` file
- Or kill the process: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess`

### "Prisma Client not generated"
- Run: `npm run db:generate`

## 📖 Learning Resources

- [Express.js Docs](https://expressjs.com/)
- [Prisma Docs](https://www.prisma.io/docs)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

## 🤝 Next Steps

Once the backend is running, you can:
1. Test endpoints with the commands above
2. Set up the React frontend
3. Connect frontend to this API
4. Build out additional features

---

**Built with:** Express.js 4.18, Prisma 5.7, PostgreSQL
