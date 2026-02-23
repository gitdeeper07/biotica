const { createClient } = require('@supabase/supabase-js');

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

    const { source } = event.queryStringParameters || {};

    const openSources = {
      'protected-planet': {
        url: 'https://api.protectedplanet.net/v3/protected_areas',
        description: 'IUCN Protected Areas Database'
      },
      'global-forest-watch': {
        url: 'https://data.globalforestwatch.org/api/v1',
        description: 'Forest monitoring data'
      },
      'usgs-earthquake': {
        url: 'https://earthquake.usgs.gov/fdsnws/event/1/query',
        description: 'USGS Earthquake Data'
      },
      'noaa-climate': {
        url: 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data',
        description: 'NOAA Climate Data'
      },
      'worldclim': {
        url: 'https://worldclim.org/data',
        description: 'Global climate data'
      },
      'soilgrids': {
        url: 'https://rest.isric.org/soilgrids/v2.0/properties/query',
        description: 'Global soil data'
      },
      'usgs-landcover': {
        url: 'https://www.usgs.gov/centers/eros/science/national-land-cover-database',
        description: 'USGS Land Cover Database'
      },
      'esa-cci': {
        url: 'https://www.esa-landcover-cci.org/',
        description: 'ESA Climate Change Initiative Land Cover'
      },
      'modis': {
        url: 'https://modis.gsfc.nasa.gov/data/',
        description: 'MODIS Satellite Data'
      },
      'sentinel': {
        url: 'https://scihub.copernicus.eu/',
        description: 'Sentinel Satellite Data'
      }
    };

    if (source && openSources[source]) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          source: openSources[source],
          status: 'ready',
          note: 'Use this endpoint to fetch real data'
        })
      };
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        sources: openSources,
        message: 'Select a source to fetch data',
        total_sources: Object.keys(openSources).length
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
