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

    if (!supabaseUrl || !supabaseServiceKey) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify([])
      };
    }

    const supabase = createClient(supabaseUrl, supabaseServiceKey);
    
    const { data, error } = await supabase
      .from('specimens')
      .select('specimen_id, name, group_name, classification, emi, latitude, longitude')
      .order('emi', { ascending: false });

    if (error) {
      console.error('Supabase error:', error);
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify([])
      };
    }

    const mappedData = (data || []).map(item => ({
      specimen_id: item.specimen_id,
      name: item.name,
      group_name: item.group_name,
      group: item.group_name,
      classification: item.classification,
      emi: item.emi,
      lat: item.latitude,
      lng: item.longitude
    }));

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(mappedData)
    };

  } catch (error) {
    console.error('Error:', error);
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify([])
    };
  }
};
