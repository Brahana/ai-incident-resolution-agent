
from knowledge_base import search_troubleshooting_guide


def search_error_guide(error_message: str) -> dict:
    """Search the troubleshooting guide for a given error."""
    return search_troubleshooting_guide(error_message)
