from google.cloud import bigquery
import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="cc-project-2-key.json"

client = bigquery.Client()
project = client.project
dataset_ref = bigquery.DatasetReference(project, 'cc_project2')

table_ref = dataset_ref.table("tweets")
schema = [
    bigquery.SchemaField("name", "STRING"),
    bigquery.SchemaField("tweet", "STRING"),
    bigquery.SchemaField("sentiment", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("date", "DATE"),
    # bigquery.SchemaField("timestamp", "TIMESTAMP"),
]
table = bigquery.Table(table_ref, schema=schema)
table.time_partitioning = bigquery.TimePartitioning(
    type_=bigquery.TimePartitioningType.DAY,
    field="date", 
    expiration_ms=7776000000,
) 

table = client.create_table(table)

print(
    "Created table {}, partitioned on column {}".format(
        table.table_id, table.time_partitioning.field
    )
)