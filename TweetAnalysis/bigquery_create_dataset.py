from google.cloud import bigquery
import os 
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="cc-project-2-key.json"

# Construct a BigQuery client object.
client = bigquery.Client()

dataset_name = 'cc_project2'
# TODO(developer): Set dataset_id to the ID of the dataset to create.
dataset_id = "{}.{}".format(client.project, dataset_name)

# Construct a full Dataset object to send to the API.
dataset = bigquery.Dataset(dataset_id)

# TODO(developer): Specify the geographic location where the dataset should reside.
dataset.location = "US"

# Send the dataset to the API for creation, with an explicit timeout.
# Raises google.api_core.exceptions.Conflict if the Dataset already
# exists within the project.
dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
print("Created dataset {}.{}".format(client.project, dataset.dataset_id))