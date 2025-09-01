import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def download_prices(tickers, start, end):
    data = yf.download(tickers, start=start, end=end, progress=False, auto_adjust=True)
    if isinstance(data, pd.DataFrame) and "Close" in data.columns:
        data = data["Close"]
    data = data.dropna(how="all")
    return data

def predict_stocks(tickers, horizon_days, quality, min_prob, max_risk, stop_mult, skip_earn, skip_event):
    if isinstance(tickers, str):
        tickers = [t.strip() for t in tickers.split(",")]
    end = datetime.today()
    start = end - timedelta(days=365)
    prices = download_prices(tickers, start, end)

    results = []
    for t in tickers:
        if isinstance(prices, pd.Series):
            series = prices
        else:
            series = prices[t] if t in prices.columns else prices

        if len(series) < 50:
            results.append({"ticker": t, "error": "Not enough data"})
            continue

        ret = series.pct_change().dropna()
        mean_ret = ret.mean()
        std_ret = ret.std()

        prob_up = (ret > 0).mean()
        exp_return = mean_ret * horizon_days

        decision = "BUY" if (prob_up >= min_prob and exp_return > 0) else "HOLD"

        results.append({
            "ticker": t,
            "decision": decision,
            "prob_up": round(float(prob_up),4),
            "exp_return": round(float(exp_return),4),
            "ret_low": round(float(exp_return - 1.28*std_ret),4),
            "ret_high": round(float(exp_return + 1.28*std_ret),4),
            "auc": round(float(prob_up),4),
            "horizon_days": horizon_days,
            "reason": "" if decision=="BUY" else "Low probability or negative return"
        })

    table_md = "|Ticker|Decision|Prob Up|Exp Return%|Low%|High%|\n|---|---|---|---|---|---|\n"
    for r in results:
        if "error" in r:
            table_md += f"|{r['ticker']}|Error| | | | |\n"
        else:
            table_md += f"|{r['ticker']}|{r['decision']}|{r['prob_up']*100:.1f}%|{r['exp_return']*100:.2f}%|{r['ret_low']*100:.2f}%|{r['ret_high']*100:.2f}%|\n"

    return {
        "ok": True,
        "horizon_days": horizon_days,
        "quality": quality,
        "predictions": results,
        "table_markdown": table_md,
        "timestamp": datetime.utcnow().isoformat()+"Z"
    }

def warm_models(tickers, horizon_days, quality):
    if isinstance(tickers, str):
        tickers = [t.strip() for t in tickers.split(",")]
    end = datetime.today()
    start = end - timedelta(days=365)
    download_prices(tickers, start, end)
    return {"ok": True, "warmed": tickers}
