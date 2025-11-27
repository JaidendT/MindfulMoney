# MindfulMoney - Clean Implementation

A personal budgeting application built with Express.js, React, Prisma, and PostgreSQL.

## Backend Setup

### Prerequisites
- Node.js 18+
- PostgreSQL 17
- Git

### Installation

1. Install dependencies:
```bash
cd backend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

3. Set up database:
```bash
npx prisma db push
```

4. Start development server:
```bash
npm run dev
```

Server will run on `http://localhost:5000`

## Project Structure

```
backend/
├── src/
│   ├── server.js           # Express app entry point
│   ├── routes/             # API route handlers
│   └── controllers/        # Business logic
├── prisma/
│   └── schema.prisma       # Database schema
├── .env                    # Environment variables
└── package.json

frontend/
└── (to be created)
```

## API Endpoints (Planned)

- `GET /api/health` - Health check
- `GET /api/transactions` - Get all transactions
- `POST /api/transactions` - Create transaction
- `PUT /api/transactions/:id` - Update transaction
- `DELETE /api/transactions/:id` - Delete transaction
- `POST /api/upload` - Upload CSV file
- `GET /api/analytics/summary` - Get financial summary

## Tech Stack

**Backend:**
- Express.js 4.18
- Prisma ORM 5.7
- PostgreSQL 17
- Node.js 18+

**Frontend (Planned):**
- React 18
- Axios
- Tailwind CSS or Material-UI

## Next Steps

1. Create transaction routes
2. Implement CSV upload functionality
3. Build analytics endpoints
4. Initialize React frontend
5. Create UI components
6. Connect frontend to backend
