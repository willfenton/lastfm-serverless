import json
import logging
import os
from datetime import datetime, timedelta

import boto3
import pytz

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    timezone = os.environ["timezone"]
    now = datetime.now(pytz.timezone(timezone))

    # end of yesterday (11:59:59 PM)
    to_datetime = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
    # start of yesterday (00:00:00 AM)
    from_datetime = to_datetime - timedelta(days=1) + timedelta(seconds=1)

    logger.info(f"Time Range: {from_datetime.strftime('%c')} to {to_datetime.strftime('%c')}")

    update_lambda_event = {
        "from_uts": int(from_datetime.timestamp()),
        "to_uts": int(to_datetime.timestamp()),
    }

    logger.info(update_lambda_event)

    lambda_client = boto3.client("lambda")
    update_lambda_name = os.environ["update_lambda_name"]

    response = lambda_client.invoke(
        FunctionName=update_lambda_name,
        InvocationType="Event",
        Payload=json.dumps(update_lambda_event),
    )

    return
