const { createClient } = require('@supabase/supabase-js');

const IBR_WEIGHTS = {
  vca: 0.20,
  mdi: 0.15,
  pts: 0.12,
  hfi: 0.11,
  bnc: 0.10,
  sgh: 0.09,
  aes: 0.08,
  tmi: 0.08,
  rrc: 0.07
};

exports.handler = async (event, context) => {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;
    const supabase = createClient(supabaseUrl, supabaseServiceKey);

    const { measurement_id, parameters } = JSON.parse(event.body || '{}');

    if (!parameters) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Parameters required' })
      };
    }

    let ibr = 0;
    let totalWeight = 0;
    const contributions = {};

    for (const [param, weight] of Object.entries(IBR_WEIGHTS)) {
      if (parameters[param]) {
        const contrib = parameters[param] * weight;
        ibr += contrib;
        totalWeight += weight;
        contributions[param] = contrib;
      }
    }

    const normalizedIbr = totalWeight > 0 ? ibr / totalWeight : 0;

    let classification;
    if (normalizedIbr > 0.88) classification = 'PRISTINE';
    else if (normalizedIbr > 0.75) classification = 'FUNCTIONAL';
    else if (normalizedIbr > 0.60) classification = 'IMPAIRED';
    else if (normalizedIbr > 0.45) classification = 'DEGRADED';
    else classification = 'COLLAPSED';

    if (measurement_id) {
      const { error } = await supabase
        .from('measurements')
        .update({
          ibr: normalizedIbr,
          ibr_classification: classification
        })
        .eq('id', measurement_id);

      if (error) throw error;
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        ibr: normalizedIbr,
        classification,
        contributions,
        weights_used: totalWeight,
        timestamp: new Date().toISOString()
      })
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
