def get_category(aqi):
    """
    Return the AQI category based on the AQI value.
    """

    try:
        aqi = float(aqi)
    except (ValueError, TypeError):
        return "Unknown"

    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def get_aqi_status(aqi):
    """
    Return a short AQI status.
    """

    try:
        aqi = float(aqi)
    except (ValueError, TypeError):
        return "UNKNOWN"

    if aqi <= 50:
        return "GOOD"
    elif aqi <= 100:
        return "MODERATE"
    elif aqi <= 150:
        return "UNHEALTHY FOR SENSITIVE GROUPS"
    elif aqi <= 200:
        return "UNHEALTHY"
    elif aqi <= 300:
        return "VERY UNHEALTHY"
    else:
        return "HAZARDOUS"


def get_status_color(status):
    """
    Return a color value based on AQI status.
    """

    status = str(status).upper()

    if status == "GOOD":
        return "#00A651"

    elif status == "MODERATE":
        return "#FFD700"

    elif "SENSITIVE" in status:
        return "#FF8C00"

    elif status == "UNHEALTHY":
        return "#FF0000"

    elif "VERY UNHEALTHY" in status:
        return "#8B008B"

    elif status == "HAZARDOUS":
        return "#800000"

    return "#808080"


def get_recommendation(aqi):
    """
    Return a general recommendation based on AQI.
    """

    try:
        aqi = float(aqi)
    except (ValueError, TypeError):
        return "AQI information is unavailable. Please try again later."

    if aqi <= 50:
        return (
            "Air quality is good. It is a good time to enjoy outdoor activities."
        )

    elif aqi <= 100:
        return (
            "Air quality is acceptable. Sensitive individuals should "
            "consider reducing prolonged outdoor activity."
        )

    elif aqi <= 150:
        return (
            "Sensitive groups should reduce prolonged or heavy outdoor "
            "activity. Consider taking breaks indoors."
        )

    elif aqi <= 200:
        return (
            "Everyone should reduce prolonged outdoor activity. "
            "Sensitive individuals should avoid strenuous outdoor activities."
        )

    elif aqi <= 300:
        return (
            "Avoid prolonged outdoor activity. Sensitive individuals "
            "should remain indoors when possible."
        )

    else:
        return (
            "Avoid outdoor activity as much as possible. "
            "Keep windows closed and follow local health guidance."
        )


def get_advice(aqi):
    """
    Return additional health advice based on AQI.
    """

    try:
        aqi = float(aqi)
    except (ValueError, TypeError):
        return "AQI information is unavailable."

    if aqi <= 50:
        return "Normal outdoor activities are generally suitable."

    elif aqi <= 100:
        return "People with respiratory sensitivity should monitor symptoms."

    elif aqi <= 150:
        return "Sensitive groups should consider limiting strenuous outdoor activities."

    elif aqi <= 200:
        return "Consider wearing a suitable mask outdoors and reduce strenuous activity."

    elif aqi <= 300:
        return "Avoid strenuous outdoor activities and spend more time indoors."

    else:
        return "Stay indoors as much as possible and follow official health advisories."


def get_precautions(aqi):
    """
    Return precautions based on AQI.
    """

    try:
        aqi = float(aqi)
    except (ValueError, TypeError):
        return [
            "Check the AQI again later.",
            "Follow local air-quality advisories."
        ]

    if aqi <= 50:
        return [
            "Enjoy normal outdoor activities.",
            "Continue regular healthy habits."
        ]

    elif aqi <= 100:
        return [
            "Sensitive people should monitor their health.",
            "Avoid very prolonged outdoor activity if uncomfortable."
        ]

    elif aqi <= 150:
        return [
            "Reduce prolonged outdoor activity.",
            "Sensitive groups should take more frequent breaks indoors."
        ]

    elif aqi <= 200:
        return [
            "Reduce outdoor activity.",
            "Avoid strenuous exercise outdoors.",
            "Sensitive groups should stay indoors when possible."
        ]

    elif aqi <= 300:
        return [
            "Avoid prolonged outdoor activity.",
            "Keep indoor air as clean as possible.",
            "Avoid strenuous outdoor exercise."
        ]

    else:
        return [
            "Avoid outdoor activity.",
            "Stay indoors as much as possible.",
            "Follow official health advisories."
        ]
