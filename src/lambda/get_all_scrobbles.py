import logging
import os
from datetime import datetime, timedelta
import pytz
import boto3
import json
import lastfm
import requests
import math

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def lambda_handler(event, context):
    timezone = os.environ["timezone"]
    username = os.environ["lastfm_user"]
    api_key = lastfm.get_api_key()
    concurrency = 10

    from_uts = 0
    to_uts = int(
        (
            datetime.now(pytz.timezone(timezone)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            - timedelta(seconds=1)
        ).timestamp()
    )

    page = requests.get(
        f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={api_key}&user={username}&format=json&page=1&limit=1&from={from_uts}&to={to_uts}"
    ).json()
    num_scrobbles = int(page["recenttracks"]["@attr"]["total"])
    num_pages = math.ceil(num_scrobbles / 200)
    pages = chunks([i for i in range(1, num_pages + 1)], concurrency)
    logger.info(from_uts, to_uts, num_scrobbles, num_pages, pages)

    lambda_client = boto3.client("lambda")
    update_lambda_name = os.environ["update_lambda_name"]

    for page_chunk in pages:
        event = {"from_uts": from_uts, "to_uts": to_uts, "pages": page_chunk}
        logger.info(event)
        response = lambda_client.invoke(
            FunctionName=update_lambda_name,
            InvocationType="Event",
            Payload=json.dumps(event),
        )
        logger.info(response)

    return {"key": "value"}
