from flask import Flask, request, jsonify
import os
from model import predict_stocks, warm_models

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    api_key = request.headers.get("X-API-Key")
    if api_key != os.environ.get("API_KEY"):
        return jsonify({"error": "Unauthorized"}), 401

    tickers = data.get("tickers") or data.get("ticker")
    horizon_days = data.get("horizon_days", 3)
    quality = data.get("quality", "accurate")
    min_prob = data.get("min_prob_to_trade", 0.58)
    max_risk = data.get("max_risk_per_trade", 0.0075)
    stop_mult = data.get("stop_atr_mult", 1.2)
    skip_earn = data.get("skip_earnings_window", 0)
    skip_event = data.get("skip_event_window", 0)

    result = predict_stocks(tickers, horizon_days, quality, min_prob, max_risk, stop_mult, skip_earn, skip_event)
    return jsonify(result)

@app.route("/warm", methods=["POST"])
def warm():
    data = request.get_json(force=True)
    api_key = request.headers.get("X-API-Key")
    if api_key != os.environ.get("API_KEY"):
        return jsonify({"error": "Unauthorized"}), 401

    tickers = data.get("tickers")
    horizon_days = data.get("horizon_days", 3)
    quality = data.get("quality", "accurate")
    result = warm_models(tickers, horizon_days, quality)
    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})
