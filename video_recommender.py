from urllib.parse import quote_plus

def recommend_videos(topics):
    """Map each topic to a YouTube search link."""
    base_url = "https://www.youtube.com/results?search_query="
    return {topic: f"{base_url}{quote_plus(topic)}" for topic in topics}
