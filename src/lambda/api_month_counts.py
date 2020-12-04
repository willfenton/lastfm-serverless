import csv
import datetime
import json
import logging
from io import StringIO

import boto3
import pytz

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    lastfm_username = event["queryStringParameters"]["lastfm_username"]

    bucket_name = "lastfm-serverless-athena-output"
    prefix = f"{lastfm_username}/get_month_counts/"

    s3 = boto3.resource("s3")
    bucket = s3.Bucket(name=bucket_name)

    objects = bucket.objects.filter(Prefix=prefix)
    sorted_objects = [
        obj
        for obj in sorted(objects, key=lambda obj: int(obj.last_modified.strftime("%s")))
        if obj.key.endswith(".csv")
    ]
    last_added = sorted_objects[-1]

    logger.info(last_added.key)

    month_counts_csv = last_added.get()["Body"].read().decode("utf-8")

    return {
        "headers": {"Content-Type": "text/csv"},
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": month_counts_csv,
    }
