import os
from google.cloud import pubsub_v1
from google.cloud import storage
from datetime import datetime, timezone

# Configuration (use env vars, not hardcoded)
PROJECT_ID = os.environ["PROJECT_ID"]
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
LOG_OBJECT = "forbidden_logs/forbidden_requests.log"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)


def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    text = message.data.decode("utf-8")

    timestamp = datetime.now(timezone.utc).isoformat()
    log_line = f"[{timestamp}] {text}\n"

    # 1️⃣ Print to stdout
    print(log_line.strip())

    # 2️⃣ Append to GCS file
    blob = bucket.blob(LOG_OBJECT)
    existing = blob.download_as_text() if blob.exists() else ""
    blob.upload_from_string(existing + log_line)

    message.ack()


print("Listening for forbidden requests...")
subscriber.subscribe(subscription_path, callback=callback)

# Keep process alive
import time
while True:
    time.sleep(60)
