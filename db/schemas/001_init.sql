CREATE TABLE IF NOT EXISTS prices(
    ticker TEXT,
    date DATE,
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    volume FLOAT,
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS features(
    ticker TEXT, date DATE,
    momentum_3m FLOAT, momentum_6m FLOAT, momentum_12m FLOAT,
    rsi FLOAT, macd_slope FLOAT, adx FLOAT,
    volatility_30d FLOAT, vol_compression FLOAT,
    relative_strength FLOAT, beta FLOAT,
    macro_regime TEXT, market_breadth FLOAT,
    sentiment_score FLOAT, sentiment_momentum FLOAT,
    sentiment_surprise FLOAT, news_volume FLOAT,
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS signals(
    id SERIAL PRIMARY KEY, ticker TEXT, date DATE,
    regime TEXT, alpha_score FLOAT,
    factor_vector JSONB, weights_vector JSONB,
    suggested_action TEXT, confidence FLOAT
);

CREATE TABLE IF NOT EXISTS outcomes(
    signal_id INT,
    return_3m FLOAT, return_6m FLOAT,
    max_drawdown FLOAT, volatility FLOAT,
    success_label BOOLEAN
);

CREATE TABLE IF NOT EXISTS weights(
    ticker TEXT, regime TEXT,
    w_momentum FLOAT, w_technical FLOAT,
    w_volatility FLOAT, w_macro FLOAT,
    w_behavioral FLOAT, w_sentiment FLOAT,
    last_updated DATE,
    PRIMARY KEY (ticker, regime)
);
