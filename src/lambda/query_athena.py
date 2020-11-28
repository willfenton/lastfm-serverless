import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    lastfm_username = event["lastfm_username"]

    athena_database = os.environ["athena_database"]
    output_bucket = os.environ["output_bucket"]

    output_location = f"s3://{output_bucket}/{lastfm_username}/top-albums/"

    sql_query = f"""
SELECT *
FROM top_albums_{lastfm_username}
WHERE album_count >= 20 AND num_tracks > 1
ORDER BY album_count DESC
""".strip(
        "\n"
    )

    athena_client = boto3.client("athena")

    response = athena_client.start_query_execution(
        QueryString=sql_query,
        QueryExecutionContext={"Database": athena_database},
        ResultConfiguration={"OutputLocation": output_location},
    )

    logger.info(response)

    query_execution_id = response["QueryExecutionId"]

    return
