// get-config.js - BIOTICA Config API
exports.handler = async function(event, context) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  try {
    const config = {
      supabaseUrl: process.env.SUPABASE_URL || null,
      supabaseKey: process.env.SUPABASE_SERVICE_KEY || null,
      configured: !!(process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_KEY),
      project: 'BIOTICA',
      version: '1.0.0',
      endpoints: {
        sites: '/.netlify/functions/sites',
        parameters: '/.netlify/functions/parameters',
        alerts: '/.netlify/functions/alerts',
        stats: '/.netlify/functions/stats'
      }
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(config)
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
