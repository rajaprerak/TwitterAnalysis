from google.api_core import retry
from google.cloud import pubsub_v1
import json
import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="cc-project-2-key.json"

# TODO(developer)
project_id = "certain-torus-307806"
subscription_id = "cc_project2"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

NUM_MESSAGES = 100

# Wrap the subscriber in a 'with' block to automatically call close() to
# close the underlying gRPC channel when done.
with subscriber:
    # The subscriber pulls a specific number of messages. The actual
    # number of messages pulled may be smaller than max_messages.
    response = subscriber.pull(
        request={"subscription": subscription_path, "max_messages": NUM_MESSAGES},
        retry=retry.Retry(deadline=300),
    )

    ack_ids = []
    for received_message in response.received_messages:
        # print(f"Received: {received_message.message.data}.")
        tweet = received_message.message.data
        extracted_tweet = tweet.decode("utf-8")
        tweet_dictionary = json.loads(extracted_tweet)
        ack_ids.append(received_message.ack_id)

    # Acknowledges the received messages so they will not be sent again.
    subscriber.acknowledge(
        request={"subscription": subscription_path, "ack_ids": ack_ids}
    )

    print(
        f"Received and acknowledged {len(response.received_messages)} messages from {subscription_path}."
    )