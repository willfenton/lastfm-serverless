import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sql_queries = {
    "get_top_albums": r"""
SELECT *
FROM top_albums_{lastfm_username}
WHERE album_count >= 20 AND num_tracks > 1
ORDER BY album_count DESC
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
    "create_view_top_albums": r"""
CREATE OR REPLACE VIEW "top_albums_{lastfm_username}" AS
WITH
query1 (album_name, artist_name, count, num_tracks, first_uts, last_uts) AS
(
    SELECT album_name, artist_name, COUNT(*), COUNT(DISTINCT track_name), MIN(unix_timestamp), MAX(unix_timestamp)
    FROM scrobbles_{lastfm_username}
    GROUP BY  album_name, artist_name
),
query2 (album_name, artist_name, track_name, count, album_art_url) AS
(
    SELECT album_name, artist_name, track_name, COUNT(*), album_art_url
    FROM scrobbles_{lastfm_username}
    GROUP BY  album_name, artist_name, track_name, album_art_url
),
query3 (album_name, artist_name, track_name, album_count, track_count, num_tracks, rank, first_uts, last_uts, album_art_url) AS
(
    SELECT q2.album_name, q2.artist_name, q2.track_name, q1.count, q2.count, q1.num_tracks, ROW_NUMBER() OVER(PARTITION BY q2.album_name, q2.artist_name ORDER BY  q2.count DESC), q1.first_uts, q1.last_uts, q2.album_art_url
    FROM ( query1 q1 JOIN query2 q2 ON q1.album_name = q2.album_name AND q1.artist_name = q2.artist_name )
)
SELECT album_name, artist_name, track_name, album_count, track_count, num_tracks, first_uts, last_uts, album_art_url
FROM query3
WHERE rank = 1
""",
}


def lambda_handler(event, context):
    logger.info(event)

    lastfm_usernames = event["lastfm_usernames"]
    sql_query = sql_queries[event["query"]]

    athena_database = os.environ["athena_database"]
    data_bucket = os.environ["data_bucket"]
    output_bucket = os.environ["output_bucket"]

    athena_client = boto3.client("athena")

    for lastfm_username in lastfm_usernames:
        output_location = f"s3://{output_bucket}/{lastfm_username}/{event['query']}/"

        sql_query_string = (
            sql_query.replace("{lastfm_username}", lastfm_username)
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

    return
