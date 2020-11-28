import json
import logging
import csv
from io import StringIO

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    bucket_name = "lastfm-serverless-data"
    prefix = "lastfm_serverless_get_top_albums"

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

    top_albums_csv = last_added.get()["Body"].read().decode("utf-8")

    reader = csv.DictReader(StringIO(top_albums_csv))
    output = {"albums": [album for album in reader]}

    for album in output["albums"]:
        album["album_count"] = int(album["album_count"])
        album["track_count"] = int(album["track_count"])
        album["num_tracks"] = int(album["num_tracks"])
        album["first_uts"] = int(album["first_uts"])
        album["last_uts"] = int(album["last_uts"])

    return json.dumps(output)
