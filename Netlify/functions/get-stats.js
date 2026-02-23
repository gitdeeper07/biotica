// get-stats.js - BIOTICA Statistics API
const { createClient } = require('@supabase/supabase-js');

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
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

    if (!supabaseUrl || !supabaseServiceKey) {
      // Return mock data if no database configured
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'operational',
          version: '1.0.0',
          project: 'BIOTICA',
          metrics: {
            total_sites: 25,
            mean_ibr: 0.78,
            pristine: 6,
            functional: 10,
            impaired: 6,
            degraded: 3,
            collapsed: 0,
            alerts: 0
          },
          timestamp: new Date().toISOString()
        })
      };
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    // Get sites data
    const { data: sites, error: sitesError } = await supabase
      .from('sites')
      .select('*');

    if (sitesError) throw sitesError;

    // Get alerts
    const { data: alerts, error: alertsError } = await supabase
      .from('alerts')
      .select('*')
      .eq('status', 'active');

    if (alertsError) throw alertsError;

    // Calculate statistics
    const total = sites.length;
    const meanIbr = sites.reduce((sum, s) => sum + s.ibr, 0) / total;
    
    const counts = {
      pristine: sites.filter(s => s.classification === 'PRISTINE').length,
      functional: sites.filter(s => s.classification === 'FUNCTIONAL').length,
      impaired: sites.filter(s => s.classification === 'IMPAIRED').length,
      degraded: sites.filter(s => s.classification === 'DEGRADED').length,
      collapsed: sites.filter(s => s.classification === 'COLLAPSED').length
    };

    const stats = {
      status: 'operational',
      version: '1.0.0',
      project: 'BIOTICA',
      metrics: {
        total_sites: total,
        mean_ibr: Number(meanIbr.toFixed(2)),
        ...counts,
        alerts: alerts.length,
        recovery_rate: 100 - ((counts.collapsed + counts.degraded) / total * 100)
      },
      timestamp: new Date().toISOString()
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(stats, null, 2)
    };

  } catch (error) {
    console.error('Error:', error);

    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal Server Error',
        message: error.message
      })
    };
  }
};
