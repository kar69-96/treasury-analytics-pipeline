const { Pool } = require('pg');

// Convert array of objects to CSV
function toCSV(data) {
  if (!data || data.length === 0) {
    return '';
  }
  
  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV header row
  const headerRow = headers.join(',');
  
  // Create data rows
  const dataRows = data.map(row => {
    return headers.map(header => {
      const value = row[header];
      // Escape values that contain commas, quotes, or newlines
      if (value === null || value === undefined) {
        return '';
      }
      const stringValue = String(value);
      if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
        return `"${stringValue.replace(/"/g, '""')}"`;
      }
      return stringValue;
    }).join(',');
  });
  
  return [headerRow, ...dataRows].join('\n');
}

module.exports = async (req, res) => {
  // Enable CORS for Excel
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  
  const postgresUrl = process.env.POSTGRES_URL;
  
  if (!postgresUrl) {
    return res.status(500).json({ error: 'POSTGRES_URL not configured' });
  }

  try {
    const pool = new Pool({
      connectionString: postgresUrl,
      ssl: { rejectUnauthorized: false }
    });

    const result = await pool.query('SELECT * FROM fact_interest_rates_daily ORDER BY date DESC');
    await pool.end();

    // Check if JSON format is explicitly requested
    const format = req.query.format || req.headers.accept;
    if (format && format.includes('application/json')) {
      res.setHeader('Content-Type', 'application/json');
      res.status(200).json(result.rows);
    } else {
      // Default to CSV format for Excel compatibility
      res.setHeader('Content-Type', 'text/csv');
      const csv = toCSV(result.rows);
      res.status(200).send(csv);
    }
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ error: error.message });
  }
};
