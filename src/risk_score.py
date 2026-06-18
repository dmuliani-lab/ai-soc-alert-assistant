def calculate_risk_score(attack_probability, severity=0.8, asset_criticality=0.7):
    """
    Calculate a SOC triage risk score.

    Formula:
    Risk Score = 0.55 * Attack Probability + 0.25 * Severity
                 + 0.20 * Asset Criticality

    In a real SOC environment these weights should be tuned using historical
    incidents, asset criticality, business impact, and analyst feedback.
    """
    score = (
        0.55 * float(attack_probability)
        + 0.25 * float(severity)
        + 0.20 * float(asset_criticality)
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
