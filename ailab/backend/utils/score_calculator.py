def calculate_score(market_demand: int, competition: int, difficulty: int, monetization: int) -> float:
    weighted = (market_demand * 0.35) + ((11 - competition) * 0.2) + ((11 - difficulty) * 0.15) + (monetization * 0.3)
    return round(weighted, 1)
