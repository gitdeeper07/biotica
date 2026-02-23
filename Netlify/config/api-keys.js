// STALWART Database Connection Configuration
// Bridge Health Monitoring System

const DB_KEYS = {
  // PostgreSQL Connection (Supabase/Neon/Railway)
  DATABASE_URL: process.env.DATABASE_URL || 'postgresql://postgres:password@localhost:5432/stalwart',
  
  // Supabase Connection (إذا كنت تستخدم Supabase)
  SUPABASE_URL: process.env.SUPABASE_URL || 'https://your-project.supabase.co',
  SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY || 'your-anon-key',
  SUPABASE_SERVICE_ROLE_KEY: process.env.SUPABASE_SERVICE_ROLE_KEY || 'your-service-role-key',
  
  // Neon PostgreSQL (Serverless)
  NEON_DATABASE_URL: process.env.NEON_DATABASE_URL || 'postgresql://user:password@ep-your-project.neon.tech/neondb',
  
  // Railway.app
  RAILWAY_DATABASE_URL: process.env.RAILWAY_DATABASE_URL || 'postgresql://postgres:password@containers-us-west.railway.app:5432/railway',
  
  // Connection Pool Settings
  POOL_MAX: 20,
  POOL_MIN: 5,
  POOL_IDLE_TIMEOUT: 10000,
  POOL_CONNECTION_TIMEOUT: 2000,
  
  // SSL Configuration (للاتصالات الآمنة)
  SSL_ENABLED: process.env.NODE_ENV === 'production',
  SSL_REJECT_UNAUTHORIZED: false,
  
  // Environment
  NODE_ENV: process.env.NODE_ENV || 'development',
  STALWART_VERSION: '2.0.0'
};

// جداول قاعدة البيانات
const DB_TABLES = {
  bridge_systems: 'bridge_systems',
  bridge_spans: 'bridge_spans',
  sensors: 'sensors',
  sensor_readings: 'sensor_readings',
  computed_metrics: 'computed_metrics',
  alerts: 'alerts',
  csz_events: 'csz_events',
  inspections: 'inspections',
  maintenance_actions: 'maintenance_actions',
  traffic_events: 'traffic_events',
  weather_events: 'weather_events',
  reports: 'reports',
  ml_predictions: 'ml_predictions'
};

module.exports = { DB_KEYS, DB_TABLES };
