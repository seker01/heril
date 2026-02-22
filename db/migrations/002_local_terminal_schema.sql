CREATE TABLE IF NOT EXISTS stocks (
    ticker TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    meta_label TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS price_history (
    ticker TEXT REFERENCES stocks(ticker),
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    market_regime TEXT,
    macro_snapshot JSONB,
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT REFERENCES stocks(ticker),
    prediction_date DATE NOT NULL,
    horizon TEXT CHECK (horizon IN ('7d','30d','90d')) NOT NULL,
    predicted_return FLOAT NOT NULL,
    predicted_direction TEXT CHECK (predicted_direction IN ('UP','DOWN','FLAT')) NOT NULL,
    feature_snapshot JSONB NOT NULL,
    model_version TEXT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS prediction_results (
    prediction_id BIGINT PRIMARY KEY REFERENCES predictions(id),
    evaluated_at TIMESTAMP DEFAULT NOW(),
    actual_return FLOAT,
    accuracy FLOAT,
    is_correct BOOLEAN,
    error_magnitude FLOAT
);

CREATE TABLE IF NOT EXISTS sentiment_scores (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT REFERENCES stocks(ticker),
    score_date DATE NOT NULL,
    news_polarity FLOAT,
    social_sentiment FLOAT,
    volume_spike FLOAT,
    geopolitical_signal FLOAT,
    composite_score FLOAT,
    source_payload JSONB,
    UNIQUE (ticker, score_date)
);

CREATE TABLE IF NOT EXISTS model_weights (
    id BIGSERIAL PRIMARY KEY,
    ticker TEXT,
    regime TEXT,
    model_version TEXT,
    weights JSONB NOT NULL,
    reinforcement_score FLOAT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (ticker, regime, model_version)
);

CREATE TABLE IF NOT EXISTS root_cause_analysis (
    id BIGSERIAL PRIMARY KEY,
    prediction_id BIGINT REFERENCES predictions(id),
    main_failure_reason TEXT,
    missed_driver TEXT,
    weak_signal TEXT,
    overweighted_signal TEXT,
    suggested_weight_adjustments JSONB,
    confidence FLOAT,
    llm_model TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (prediction_id)
);
