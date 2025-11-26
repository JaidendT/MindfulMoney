/**
 * Transaction Routes
 * 
 * API endpoints for managing transactions:
 * - GET    /api/transactions       - Get all transactions
 * - GET    /api/transactions/:id   - Get single transaction
 * - POST   /api/transactions       - Create new transaction
 * - PUT    /api/transactions/:id   - Update transaction
 * - DELETE /api/transactions/:id   - Delete transaction
 */

import express from 'express';
import { PrismaClient } from '@prisma/client';

const router = express.Router();
const prisma = new PrismaClient();

/**
 * GET /api/transactions
 * Get all transactions, ordered by date (newest first)
 */
router.get('/', async (req, res, next) => {
  try {
    const transactions = await prisma.transaction.findMany({
      orderBy: {
        date: 'desc'
      }
    });
    
    res.json({
      success: true,
      count: transactions.length,
      data: transactions
    });
  } catch (error) {
    next(error);
  }
});

/**
 * GET /api/transactions/:id
 * Get a single transaction by ID
 */
router.get('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    
    const transaction = await prisma.transaction.findUnique({
      where: { id: parseInt(id) }
    });
    
    if (!transaction) {
      return res.status(404).json({
        success: false,
        error: 'Transaction not found'
      });
    }
    
    res.json({
      success: true,
      data: transaction
    });
  } catch (error) {
    next(error);
  }
});

/**
 * POST /api/transactions
 * Create a new transaction
 * 
 * Body: { date, description, amount, balance?, category? }
 */
router.post('/', async (req, res, next) => {
  try {
    const { date, description, amount, balance, category } = req.body;
    
    // Validation
    if (!date || amount === undefined) {
      return res.status(400).json({
        success: false,
        error: 'Date and amount are required'
      });
    }
    
    // Create transaction using Prisma
    // Prisma automatically handles SQL injection through parameterized queries
    const transaction = await prisma.transaction.create({
      data: {
        date: new Date(date),
        description,
        amount: parseFloat(amount),
        balance: balance ? parseFloat(balance) : null,
        category
      }
    });
    
    res.status(201).json({
      success: true,
      data: transaction
    });
  } catch (error) {
    next(error);
  }
});

/**
 * PUT /api/transactions/:id
 * Update an existing transaction
 */
router.put('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    const { date, description, amount, balance, category } = req.body;
    
    const transaction = await prisma.transaction.update({
      where: { id: parseInt(id) },
      data: {
        ...(date && { date: new Date(date) }),
        ...(description !== undefined && { description }),
        ...(amount !== undefined && { amount: parseFloat(amount) }),
        ...(balance !== undefined && { balance: balance ? parseFloat(balance) : null }),
        ...(category !== undefined && { category })
      }
    });
    
    res.json({
      success: true,
      data: transaction
    });
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({
        success: false,
        error: 'Transaction not found'
      });
    }
    next(error);
  }
});

/**
 * DELETE /api/transactions/:id
 * Delete a transaction
 */
router.delete('/:id', async (req, res, next) => {
  try {
    const { id } = req.params;
    
    await prisma.transaction.delete({
      where: { id: parseInt(id) }
    });
    
    res.json({
      success: true,
      message: 'Transaction deleted successfully'
    });
  } catch (error) {
    if (error.code === 'P2025') {
      return res.status(404).json({
        success: false,
        error: 'Transaction not found'
      });
    }
    next(error);
  }
});

export default router;
