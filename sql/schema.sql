CREATE TABLE IF NOT EXISTS stocks (
  id BIGSERIAL PRIMARY KEY,
  symbol VARCHAR(20) UNIQUE NOT NULL,
  name TEXT,
  sector VARCHAR(100),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks(symbol);

CREATE TABLE IF NOT EXISTS watchlist (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id),
  is_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_watchlist_stock_id ON watchlist(stock_id);

CREATE TABLE IF NOT EXISTS price_history (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id),
  ts TIMESTAMPTZ NOT NULL,
  open NUMERIC(18,6), high NUMERIC(18,6), low NUMERIC(18,6), close NUMERIC(18,6),
  volume BIGINT,
  source VARCHAR(50) DEFAULT 'yfinance',
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(stock_id, ts)
);
CREATE INDEX IF NOT EXISTS idx_price_stock_ts ON price_history(stock_id, ts DESC);

CREATE TABLE IF NOT EXISTS news (
  id BIGSERIAL PRIMARY KEY,
  source VARCHAR(150), title TEXT, summary TEXT, url TEXT UNIQUE,
  published_at TIMESTAMPTZ, raw_payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at DESC);

CREATE TABLE IF NOT EXISTS kap_announcements (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id),
  title TEXT, summary TEXT, url TEXT UNIQUE,
  published_at TIMESTAMPTZ, raw_payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kap_stock_published ON kap_announcements(stock_id, published_at DESC);

CREATE TABLE IF NOT EXISTS macro_events (
  id BIGSERIAL PRIMARY KEY,
  event_type VARCHAR(100), title TEXT, summary TEXT,
  event_time TIMESTAMPTZ, source VARCHAR(100), raw_payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_macro_time ON macro_events(event_time DESC);

CREATE TABLE IF NOT EXISTS llm_analysis (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id),
  event_source VARCHAR(30), event_id BIGINT,
  is_relevant BOOLEAN, impact_direction VARCHAR(20), impact_strength VARCHAR(20),
  time_horizon VARCHAR(20), reasoning TEXT, affected_factors JSONB,
  confidence_score INT CHECK (confidence_score BETWEEN 0 AND 100),
  risk_level VARCHAR(20), alternative_scenarios JSONB, analysis_payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_llm_stock_time ON llm_analysis(stock_id, created_at DESC);

CREATE TABLE IF NOT EXISTS alerts (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id),
  llm_analysis_id BIGINT REFERENCES llm_analysis(id),
  status VARCHAR(20) DEFAULT 'pending', alert_message TEXT,
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_alerts_stock_created ON alerts(stock_id, created_at DESC);

CREATE TABLE IF NOT EXISTS alert_logs (
  id BIGSERIAL PRIMARY KEY,
  alert_id BIGINT REFERENCES alerts(id),
  channel VARCHAR(20), success BOOLEAN, response TEXT,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS historical_reactions (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id),
  event_ref VARCHAR(60), move_date DATE, pct_change NUMERIC(8,4),
  reaction_type VARCHAR(30), notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_hist_stock_move_date ON historical_reactions(stock_id, move_date DESC);

CREATE TABLE IF NOT EXISTS market_regimes (
  id BIGSERIAL PRIMARY KEY,
  regime_name VARCHAR(50), start_date DATE, end_date DATE,
  volatility_score NUMERIC(8,4), trend_label VARCHAR(20), meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS model_weights (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id), feature_name VARCHAR(120),
  weight NUMERIC(14,6), model_version VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(stock_id, feature_name, model_version)
);

CREATE TABLE IF NOT EXISTS prediction_results (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT REFERENCES stocks(id),
  backtest_window VARCHAR(30), accuracy NUMERIC(8,4), avg_return NUMERIC(8,4),
  false_positives INT, win_rate NUMERIC(8,4), payload JSONB,
  created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_pred_stock_created ON prediction_results(stock_id, created_at DESC);
