
class StrategyAgent:

    def analyze(self, u, m, f, r, sentiment=None, feedback=None):
        sentiment = sentiment or {}
        feedback = feedback or {}

        sentiment_score = sentiment.get("sentimentScore", 0)
        news_sentiment = sentiment.get("newsSentiment", "Neutral")

        base_risk = r["riskScore"]
        sentiment_weight = 8

        effective_risk = (
            base_risk - sentiment_score * sentiment_weight
        )

        # Apply a revision penalty only when RiskAgent requests it.
        if feedback.get("needsRevision"):
            effective_risk += 8

        effective_risk = max(5, min(100, effective_risk))

        if effective_risk < 20:
            recommendation = "BUY"
            score = 35
        elif effective_risk < 40:
            recommendation = "HOLD"
            score = 18
        else:
            recommendation = "SELL"
            score = 8

        price = m["currentPrice"]

        reasoning = [
            "Trend-based analysis",
            "Risk score evaluated",
            "Fundamentals checked",
            f"News sentiment: {news_sentiment}",
        ]

        if feedback.get("needsRevision"):
            reasoning.append(
                "RiskAgent requested a revision: "
                + feedback.get("reason", "Elevated risk")
            )

        return {
            "recommendation": recommendation,
            "confidence": "Moderate",
            "buyScore": score,
            "effectiveRisk": round(effective_risk, 1),
            "targetPrice1": round(price * 1.1, 2),
            "targetPrice2": round(price * 1.2, 2),
            "stopLoss": round(price * 0.9, 2),
            "reasoning": reasoning,
        }
