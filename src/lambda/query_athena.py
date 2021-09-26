import logging
import os
import re
import time

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sql_queries = {
    "get_all_scrobbles": r"""
SELECT *
FROM scrobbles_{lastfm_username}
""",
    "create_table": r"""
CREATE EXTERNAL TABLE IF NOT EXISTS {database_name}.scrobbles_{lastfm_username} (
  `track_name` string,
  `album_name` string,
  `artist_name` string,
  `unix_timestamp` int,
  `album_art_url` string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "escapeChar" = "\\")
LOCATION 's3://{data_bucket}/{lastfm_username}/scrobbles/'
TBLPROPERTIES ('has_encrypted_data'='false');    
""",
}


def lambda_handler(event, context):
    logger.info(event)

    queries = event["queries"]
    lastfm_usernames = event["lastfm_usernames"]

    athena_database = os.environ["athena_database"]
    data_bucket = os.environ["data_bucket"]
    output_bucket = os.environ["output_bucket"]
    public_bucket = os.environ["public_bucket"]

    athena_client = boto3.client("athena")
    s3_client = boto3.client("s3")

    for query in queries:
        sql_query = sql_queries[query]

        for lastfm_username in lastfm_usernames:
            output_location = f"s3://{output_bucket}/{lastfm_username}/{query}/"

            sql_query_string = (
                sql_query
                    .replace("{lastfm_username}", lastfm_username)
                    .replace("{database_name}", athena_database)
                    .replace("{data_bucket}", data_bucket)
                    .strip("\n")
            )

            logger.info(f"User: {lastfm_username}")
            logger.info(f"Output Location: {output_location}")
            logger.info(f"Query String: {sql_query_string}")

            response = athena_client.start_query_execution(
                QueryString=sql_query_string,
                QueryExecutionContext={"Database": athena_database},
                ResultConfiguration={"OutputLocation": output_location},
            )

            logger.info(response)

            query_execution_id = response["QueryExecutionId"]

            state = 'RUNNING'
            retries = 10

            while retries > 0 and state in ['RUNNING', 'QUEUED']:
                retries -= 1
                response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)

                if 'QueryExecution' in response and \
                        'Status' in response['QueryExecution'] and \
                        'State' in response['QueryExecution']['Status']:

                    state = response['QueryExecution']['Status']['State']

                    if state == 'FAILED':
                        logger.info(response)
                    elif state == 'SUCCEEDED':
                        s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                        logger.info(s3_path)
                        s3_client.copy_object(
                            CopySource=re.search(r"s3://(.*)", s3_path).group(1),
                            Bucket=public_bucket,
                            Key=f"{lastfm_username}/{query}/data.csv"
                        )

                time.sleep(1)

    return
