import os
import json
from datetime import datetime, timezone

from google.cloud import storage
from google.cloud import pubsub_v1

# Forbidden export countries (as given in HW)
FORBIDDEN_COUNTRIES = {
    "North Korea", "Iran", "Cuba", "Myanmar", "Iraq",
    "Libya", "Sudan", "Zimbabwe", "Syria"
}

# Env vars set during deployment
BUCKET_NAME = os.environ["BUCKET_NAME"]              # e.g., pagerank-bu-ap178152
PREFIX = os.environ.get("PREFIX", "webgraph_v2/")    # e.g., webgraph_v2/
TOPIC_NAME = os.environ["TOPIC_NAME"]                # full topic path or name

storage_client = storage.Client()
publisher = pubsub_v1.PublisherClient()


def log_struct(event_type: str, **fields):
    """Structured log to Cloud Logging via stdout."""
    payload = {
        "event_type": event_type,
        "ts": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    print(json.dumps(payload))


def http_files(request):
    # 501 for unsupported methods
    if request.method != "GET":
        log_struct("METHOD_NOT_IMPLEMENTED", method=request.method, path=request.path)
        return ("Not Implemented", 501)

    # expected: https://domain/0.html
    # Extract ONLY the last path segment as filename
    path = (request.path or "").rstrip("/")          # "/0.html" or "/domain/0.html"
    filename = path.rsplit("/", 1)[-1].strip()       # "0.html"

    country = (request.headers.get("X-country") or "").strip()

    if not filename:
        log_struct("BAD_REQUEST", reason="missing filename", path=request.path)
        return ("Missing /<file>", 400)

    # Forbidden country => 400 + notify service2 via Pub/Sub
    if country in FORBIDDEN_COUNTRIES:
        msg = {
            "reason": "FORBIDDEN_COUNTRY",
            "country": country,
            "file": filename,
            "user_agent": request.headers.get("User-Agent", ""),
        }
        future = publisher.publish(TOPIC_NAME, json.dumps(msg).encode("utf-8"))
        future.result()
        log_struct("FORBIDDEN_REQUEST", **msg)
        return ("Permission denied (forbidden export country)", 400)

    # Read from bucket/prefix (OLD LOGIC PRESERVED)
    object_name = filename
    if PREFIX and not filename.startswith(PREFIX):
        object_name = PREFIX + filename

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(object_name)

    if not blob.exists():
        log_struct("FILE_NOT_FOUND", file=object_name, country=country)
        return ("Not Found", 404)

    data = blob.download_as_bytes()
    log_struct("FILE_SERVED", file=object_name, bytes=len(data), country=country)
    return (data, 200, {"Content-Type": "text/html"})