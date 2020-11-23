import logging
import os
from datetime import datetime, timedelta
import pytz
import boto3
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    timezone = os.environ["timezone"]

    midnight = datetime.now(pytz.timezone(timezone)).replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(seconds=1)
    last_midnight = midnight - timedelta(days=1) + timedelta(seconds=1)

    logger.info(
        f"Time Range: {last_midnight.strftime('%c')} to {midnight.strftime('%c')}"
    )

    update_lambda_event = {
        "from_uts": int(last_midnight.timestamp()),
        "to_uts": int(midnight.timestamp()),
    }

    lambda_client = boto3.client("lambda")
    update_lambda_name = os.environ["update_lambda_name"]

    response = lambda_client.invoke(
        FunctionName=update_lambda_name,
        InvocationType="Event",
        Payload=bytes(json.dumps(update_lambda_event)),
    )

    return response
