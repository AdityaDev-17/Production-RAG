import requests

API_URL = "http://localhost:8000"


def health_check():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.json()
    except Exception:
        return None


def get_metrics():
    try:
        response = requests.get(f"{API_URL}/metrics")
        return response.json()
    except Exception:
        return None


def get_cache_stats():
    try:
        response = requests.get(f"{API_URL}/cache/stats")
        return response.json()
    except Exception:
        return None


def send_message(message: str, thread_id: str):
    response = requests.post(
        f"{API_URL}/chat",
        json={
            "message": message,
            "thread_id": thread_id,
        },
    )
    response.raise_for_status()
    return response.json()