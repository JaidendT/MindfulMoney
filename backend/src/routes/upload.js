/**
 * Upload Routes
 * 
 * API endpoint for CSV file upload and transaction import
 */

import express from 'express';
import multer from 'multer';
import csv from 'csv-parser';
import fs from 'fs';
import { PrismaClient } from '@prisma/client';

const router = express.Router();
const prisma = new PrismaClient();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  }
});

const upload = multer({
  storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/csv' || file.originalname.endsWith('.csv')) {
      cb(null, true);
    } else {
      cb(new Error('Only CSV files are allowed'));
    }
  }
});

/**
 * Detect which columns contain our needed data
 */
function detectColumns(headers) {
  const headerMap = {};
  const lowerHeaders = headers.map(h => h.toLowerCase().trim());
  
  // Date column
  const dateKeywords = ['posting date', 'transaction date', 'date'];
  for (const keyword of dateKeywords) {
    const index = lowerHeaders.indexOf(keyword);
    if (index !== -1) {
      headerMap.date = headers[index];
      break;
    }
  }
  
  // Description column
  const descKeywords = ['description', 'original description', 'details'];
  for (const keyword of descKeywords) {
    const index = lowerHeaders.indexOf(keyword);
    if (index !== -1) {
      headerMap.description = headers[index];
      break;
    }
  }
  
  // Money In/Out columns
  const moneyInIndex = lowerHeaders.indexOf('money in');
  const moneyOutIndex = lowerHeaders.indexOf('money out');
  
  if (moneyInIndex !== -1) headerMap.moneyIn = headers[moneyInIndex];
  if (moneyOutIndex !== -1) headerMap.moneyOut = headers[moneyOutIndex];
  
  // Balance column
  const balanceIndex = lowerHeaders.indexOf('balance');
  if (balanceIndex !== -1) headerMap.balance = headers[balanceIndex];
  
  // Category column
  const categoryIndex = lowerHeaders.indexOf('category');
  if (categoryIndex !== -1) headerMap.category = headers[categoryIndex];
  
  return headerMap;
}

/**
 * Parse amount value, handling different formats
 */
function parseAmount(value) {
  if (!value || value === '') return null;
  
  const cleaned = String(value)
    .replace(/,/g, '')
    .replace(/R/g, '')
    .replace(/\$/g, '')
    .trim();
  
  const parsed = parseFloat(cleaned);
  return isNaN(parsed) ? null : parsed;
}

/**
 * POST /api/upload
 * Upload and import CSV file
 */
router.post('/', upload.single('file'), async (req, res, next) => {
  if (!req.file) {
    return res.status(400).json({
      success: false,
      error: 'No file uploaded'
    });
  }
  
  const results = [];
  let columnMap = null;
  let imported = 0;
  let skipped = 0;
  
  try {
    // Read and parse CSV
    await new Promise((resolve, reject) => {
      fs.createReadStream(req.file.path)
        .pipe(csv())
        .on('headers', (headers) => {
          columnMap = detectColumns(headers);
        })
        .on('data', (row) => {
          results.push(row);
        })
        .on('end', resolve)
        .on('error', reject);
    });
    
    // Validate we found required columns
    if (!columnMap || !columnMap.date) {
      throw new Error('Could not detect date column in CSV');
    }
    
    if (!columnMap.moneyIn && !columnMap.moneyOut) {
      throw new Error('Could not detect amount columns in CSV');
    }
    
    // Process each row
    for (const row of results) {
      try {
        // Parse date
        const dateValue = row[columnMap.date];
        if (!dateValue) {
          skipped++;
          continue;
        }
        const date = new Date(dateValue);
        if (isNaN(date.getTime())) {
          skipped++;
          continue;
        }
        
        // Parse amount (Money In/Out format)
        let amount = null;
        if (columnMap.moneyIn && columnMap.moneyOut) {
          const moneyIn = parseAmount(row[columnMap.moneyIn]);
          const moneyOut = parseAmount(row[columnMap.moneyOut]);
          
          if (moneyIn && moneyIn > 0) {
            amount = moneyIn;
          } else if (moneyOut) {
            amount = moneyOut; // Already negative in CSV
          }
        }
        
        if (amount === null) {
          skipped++;
          continue;
        }
        
        const description = row[columnMap.description] || '';
        const balance = columnMap.balance ? parseAmount(row[columnMap.balance]) : null;
        const category = columnMap.category ? row[columnMap.category] : null;
        
        // Check for duplicates
        const existing = await prisma.transaction.findFirst({
          where: {
            date,
            description,
            amount
          }
        });
        
        if (existing) {
          skipped++;
          continue;
        }
        
        // Create transaction
        // Prisma uses parameterized queries internally - safe from SQL injection
        await prisma.transaction.create({
          data: {
            date,
            description,
            amount,
            balance,
            category
          }
        });
        
        imported++;
      } catch (error) {
        console.error('Error processing row:', error);
        skipped++;
      }
    }
    
    // Clean up uploaded file
    fs.unlinkSync(req.file.path);
    
    res.json({
      success: true,
      message: `Imported ${imported} transactions. Skipped ${skipped} duplicates or invalid rows.`,
      data: {
        imported,
        skipped,
        total: results.length
      }
    });
  } catch (error) {
    // Clean up file on error
    if (req.file && fs.existsSync(req.file.path)) {
      fs.unlinkSync(req.file.path);
    }
    next(error);
  }
});

export default router;
