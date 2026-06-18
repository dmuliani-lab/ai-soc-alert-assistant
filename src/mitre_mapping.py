def map_alert_to_mitre(alert_data, risk_level=None):
    """
    Map a network alert to a simple MITRE ATT&CK-style category.

    This is a prototype educational mapping for a bachelor thesis project.
    It is not a full threat intelligence system and should not be used as a
    production-grade SOC detection rule set.
    """

    duration = float(alert_data.get("duration", 0))
    src_bytes = float(alert_data.get("src_bytes", 0))
    dst_bytes = float(alert_data.get("dst_bytes", 0))
    packet_count = float(alert_data.get("packet_count", 0))
    error_count = float(alert_data.get("error_count", 0))

    if packet_count >= 70 and src_bytes >= 7000 and dst_bytes <= 300:
        return {
            "tactic": "Impact",
            "technique": "DoS or DDoS-like behavior",
            "reason": (
                "High packet_count and high src_bytes with low dst_bytes may "
                "indicate service flooding or resource exhaustion behavior."
            ),
        }

    if error_count >= 10:
        return {
            "tactic": "Credential Access",
            "technique": "Brute Force-like behavior",
            "reason": (
                "High error_count may indicate repeated failed access attempts "
                "similar to brute force activity."
            ),
        }

    if duration >= 10 and packet_count >= 50:
        return {
            "tactic": "Command and Control",
            "technique": "Suspicious persistent communication",
            "reason": (
                "High duration combined with high packet_count may indicate "
                "longer suspicious communication that needs analyst review."
            ),
        }

    return {
        "tactic": "Unknown / Needs Analyst Review",
        "technique": "Unclassified suspicious behavior",
        "reason": (
            "The alert does not match the simple educational mapping rules. "
            "A SOC analyst should review the event context."
        ),
    }
