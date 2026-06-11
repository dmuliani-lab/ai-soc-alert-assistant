def calculate_risk_score(attack_probability, asset_criticality=0.7, severity=0.8):
    score = (
        0.55 * attack_probability
        + 0.25 * severity
        + 0.20 * asset_criticality
    ) * 100

    return round(score, 2)


def get_risk_level(score):
    if score >= 85:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"
