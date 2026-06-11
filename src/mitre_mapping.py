def map_alert_to_mitre(alert_data, risk_level):
    """
    Map a network alert to a simple MITRE ATT&CK-style category.

    This is a rule-based educational prototype. A real SOC system would use
    richer telemetry, threat intelligence, and validated detection logic.
    """

    duration = float(alert_data.get("duration", 0))
    src_bytes = float(alert_data.get("src_bytes", 0))
    dst_bytes = float(alert_data.get("dst_bytes", 0))
    packet_count = float(alert_data.get("packet_count", 0))
    error_count = float(alert_data.get("error_count", 0))

    if risk_level in ["Low", "Medium"]:
        return {
            "tactic": "No clear ATT&CK tactic",
            "technique": "Normal or low-risk activity",
            "reason": "ალერტის რისკი დაბალია ან საშუალო დონისაა და არ იკვეთება მკაფიო შეტევის პატერნი.",
        }

    if packet_count >= 70 and src_bytes >= 7000 and dst_bytes <= 300:
        return {
            "tactic": "Impact",
            "technique": "DoS / DDoS-like behavior",
            "reason": "packet_count და src_bytes მაღალია, ხოლო dst_bytes დაბალია. ეს შეიძლება მიუთითებდეს სერვისის გადატვირთვის მცდელობაზე.",
        }

    if error_count >= 10:
        return {
            "tactic": "Credential Access",
            "technique": "Brute Force-like behavior",
            "reason": "error_count მაღალია, რაც შეიძლება მიუთითებდეს ავტორიზაციის მრავალი წარუმატებელი მცდელობის მსგავს ქცევაზე.",
        }

    if duration >= 10 and packet_count >= 50:
        return {
            "tactic": "Command and Control",
            "technique": "Suspicious persistent communication",
            "reason": "კავშირის ხანგრძლივობა და packet_count მაღალია, რაც შეიძლება საეჭვო მუდმივ კომუნიკაციაზე მიუთითებდეს.",
        }

    return {
        "tactic": "Unknown / Needs Analyst Review",
        "technique": "Unclassified suspicious behavior",
        "reason": "სისტემამ დააფიქსირა მაღალი რისკი, თუმცა კონკრეტული შეტევის ტიპი დამატებით ანალიტიკოსის შემოწმებას საჭიროებს.",
    }
