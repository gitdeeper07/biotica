// parameters.js - BIOTICA Parameters API
const { createClient } = require('@supabase/supabase-js');

exports.handler = async (event, context) => {
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  try {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY;

    const parameters = [
      { symbol: 'VCA', name: 'Vegetative Carbon Absorption', weight: 20, value: 0.85, color: '#2E8B57' },
      { symbol: 'MDI', name: 'Microbial Diversity Index', weight: 15, value: 0.78, color: '#4682B4' },
      { symbol: 'PTS', name: 'Phenological Time Shift', weight: 12, value: 0.72, color: '#CD5C5C' },
      { symbol: 'HFI', name: 'Hydrological Flux Index', weight: 11, value: 0.68, color: '#1EDFC8' },
      { symbol: 'BNC', name: 'Biogeochemical Nutrient Cycle', weight: 10, value: 0.70, color: '#DAA520' },
      { symbol: 'SGH', name: 'Species Genetic Heterogeneity', weight: 9, value: 0.65, color: '#9B59B6' },
      { symbol: 'AES', name: 'Anthropogenic Encroachment', weight: 8, value: 0.82, color: '#E67E22' },
      { symbol: 'TMI', name: 'Trophic Metadata Integration', weight: 8, value: 0.71, color: '#3498DB' },
      { symbol: 'RRC', name: 'Regenerative Recovery Capacity', weight: 7, value: 0.63, color: '#E74C3C' }
    ];

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(parameters)
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
