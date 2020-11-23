import json
import boto3
from botocore.exceptions import ClientError
import logging
import requests
import os
import io
import csv


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_api_key():

    secret_name = os.environ["secret_name"]
    region_name = os.environ["aws_region"]

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error(e)
        raise e
    else:
        secrets = json.loads(get_secret_value_response["SecretString"])
        api_key = secrets["api_key"]
        return api_key


def get_page(api_key, page):

    username = os.environ["lastfm_user"]
    limit = 200
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={api_key}&user={username}&format=json&page={page}&limit={limit}"

    page = requests.get(url)

    return page.json()


def get_page_from_to(api_key, page, from_uts, to_uts):

    username = os.environ["lastfm_user"]
    limit = 200
    url = f"http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={api_key}&user={username}&format=json&page={page}&limit={limit}&from={from_uts}&to={to_uts}"

    page = requests.get(url)

    return page.json()


def page_to_csv_string(page):

    csv_string = io.StringIO()
    writer = csv.writer(csv_string, quoting=csv.QUOTE_NONNUMERIC)

    for scrobble in page["recenttracks"]["track"]:
        if "@attr" in scrobble and scrobble["@attr"]["nowplaying"] == "true":
            continue
        track_name = scrobble["name"]
        album_name = scrobble["album"]["#text"]
        artist_name = scrobble["artist"]["#text"]
        unix_timestamp = int(scrobble["date"]["uts"])
        writer.writerow([track_name, album_name, artist_name, unix_timestamp])

    return csv_string.getvalue()
