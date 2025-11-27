/**
 * Analytics Routes
 * 
 * API endpoints for financial analytics and summaries
 */

import express from 'express';
import { PrismaClient } from '@prisma/client';

const router = express.Router();
const prisma = new PrismaClient();

/**
 * GET /api/analytics/summary
 * Get overall financial summary
 * Returns: total income, total spending, net balance, and monthly breakdown
 */
router.get('/summary', async (req, res, next) => {
  try {
    // Get all transactions
    const transactions = await prisma.transaction.findMany();
    
    // Calculate totals
    const totalIncome = transactions
      .filter(t => t.amount > 0)
      .reduce((sum, t) => sum + t.amount, 0);
    
    const totalSpending = transactions
      .filter(t => t.amount < 0)
      .reduce((sum, t) => sum + Math.abs(t.amount), 0);
    
    const net = totalIncome - totalSpending;
    
    // Group by month using raw SQL for better performance
    const monthlyData = await prisma.$queryRaw`
      SELECT 
        TO_CHAR(date, 'YYYY-MM') as month,
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) as income,
        SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) as spending
      FROM transactions
      GROUP BY TO_CHAR(date, 'YYYY-MM')
      ORDER BY month DESC
    `;
    
    res.json({
      success: true,
      data: {
        totalIncome,
        totalSpending,
        net,
        monthly: monthlyData.map(m => ({
          month: m.month,
          income: parseFloat(m.income),
          spending: parseFloat(m.spending),
          net: parseFloat(m.income) - parseFloat(m.spending)
        }))
      }
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/analytics/categories
 * Get spending breakdown by category
 */
router.get('/categories', async (req, res, next) => {
  try {
    const categoryData = await prisma.transaction.groupBy({
      by: ['category'],
      _sum: {
        amount: true
      },
      _count: {
        id: true
      },
      where: {
        category: {
          not: null
        }
      }
    });
    
    res.json({
      success: true,
      data: categoryData.map(item => ({
        category: item.category,
        total: item._sum.amount,
        count: item._count.id
      }))
    });
  } catch (error) {
    next(error);
  }
});

export default router;
