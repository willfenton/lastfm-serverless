import json
import logging
import math
import os
from datetime import datetime, timedelta

import boto3
import pytz

import lastfm

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# splits a list into n evenly sized chunks
# https://stackoverflow.com/questions/2130016
def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def lambda_handler(event, context):
    logger.info(event)

    lastfm_username = event["lastfm_username"]

    api_key = lastfm.get_api_key()

    # how many API requests to make at once
    # this many lambdas will be run at the end, each one fetching some of the scrobble pages
    concurrency_cap = 10

    timezone = os.environ["timezone"]
    now = datetime.now(pytz.timezone(timezone))

    from_uts = 0
    to_uts = int((now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)).timestamp())

    # get # of scrobbles and calculate # of pages
    page = lastfm.get_page(api_key, lastfm_username, from_uts=from_uts, to_uts=to_uts, limit=1)
    num_scrobbles = int(page["recenttracks"]["@attr"]["total"])
    num_pages = math.ceil(num_scrobbles / 200)
    pages = list(split([i for i in range(1, num_pages + 1)], concurrency_cap))

    logger.info(f"Total: {num_scrobbles} scrobbles ({num_pages} pages)")

    lambda_client = boto3.client("lambda")
    update_lambda_name = os.environ["update_lambda_name"]

    # spawn concurrency_cap lambdas to get scrobbles
    for page_chunk in pages:
        event = {"from_uts": from_uts, "to_uts": to_uts, "pages": page_chunk, "lastfm_username": lastfm_username}
        logger.info(event)
        response = lambda_client.invoke(
            FunctionName=update_lambda_name,
            InvocationType="Event",
            Payload=json.dumps(event),
        )
        logger.info(response)

    return
