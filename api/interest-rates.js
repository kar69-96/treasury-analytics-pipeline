const { Pool } = require('pg');

module.exports = async (req, res) => {
  // Enable CORS for Excel
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Content-Type', 'application/json');

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

    res.status(200).json(result.rows);
  } catch (error) {
    console.error('Database error:', error);
    res.status(500).json({ error: error.message });
  }
};
