# MindfulMoney - Modern Full-Stack Version

Modern budgeting app built with Express.js, React, and PostgreSQL.

## 🚀 Quick Start

### Backend (Express.js + Prisma + PostgreSQL)
```powershell
cd backend
npm install
# Configure .env with your PostgreSQL credentials
npm run db:generate
npm run db:push
npm run dev  # Runs on http://localhost:5000
```

### Frontend (React)
```powershell
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

## 📁 Project Versions

- **`backend/`** - Express.js API with Prisma ORM + PostgreSQL
- **`frontend/`** - React application
- **`python-version/`** - Original Flask app (fully documented)

## 📚 Documentation

- `backend/README.md` - Backend setup and API docs
- `frontend/README.md` - React app setup (coming next)
- `python-version/README_DOCS.md` - Python version documentation

## 🔒 Security

Prisma ORM automatically prevents SQL injection through parameterized queries.

## 🛠️ Tech Stack

**Backend:**
- Express.js 4.18
- Prisma ORM 5.7
- PostgreSQL 14+
- Node.js 18+

**Frontend:**
- React 18
- React Router
- Axios
- Modern CSS

---

See individual README files in `backend/` and `frontend/` for detailed setup instructions.
