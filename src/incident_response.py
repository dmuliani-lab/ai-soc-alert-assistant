def get_incident_recommendations(risk_level, mitre_tactic):
    if risk_level == "Critical":
        return [
            "Start incident investigation immediately.",
            "Review source/destination traffic and firewall logs.",
            "Escalate the alert to a Tier 2 SOC analyst.",
            "Temporarily restrict suspicious traffic if business impact allows.",
            "Create an incident ticket and attach supporting evidence.",
        ]

    if risk_level == "High":
        return [
            "Send the alert for additional analyst review.",
            "Check related logs from the last 24 hours.",
            "Compare similar alerts across other hosts.",
            "Continue monitoring with increased attention.",
        ]

    if risk_level == "Medium":
        return [
            "Keep the alert under monitoring.",
            "Check whether similar activity repeats.",
            "Add the source or host to a watchlist if needed.",
        ]

    return [
        "No additional response is required at this stage.",
        "The alert may be closed as a low-risk event after review.",
    ]
