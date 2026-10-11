
TROUBLESHOOTING_GUIDE = {
    "Database connection timeout": {
        "possible_causes": [
            "Database server is unavailable",
            "Network connectivity issues",
            "Connection pool is exhausted",
            "Database response is slow"
        ],
        "recommended_checks": [
            "Check database server health",
            "Verify network connectivity",
            "Review database connection pool metrics",
            "Inspect database logs around the failure timestamp"
        ]
    },
    "Permission denied": {
        "possible_causes": [
            "Incorrect file or directory permissions",
            "Application running under an unexpected user"
        ],
        "recommended_checks": [
            "Check file ownership and permissions",
            "Verify the application's runtime user",
            "Review access control settings"
        ]
    }
}


def search_troubleshooting_guide(error_message):
    """Find troubleshooting guidance for a known error."""

    for known_error, guidance in TROUBLESHOOTING_GUIDE.items():
        if known_error.lower() in error_message.lower():
            return {
                "matched_error": known_error,
                **guidance
            }

    return {
        "matched_error": None,
        "message": "No matching guidance found. Investigate the error before recommending a fix."
    }
