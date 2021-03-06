import csv
import io
import json
import logging
import os

import boto3
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_api_key():
    secret_name = os.environ["secret_name"]
    region_name = os.environ["aws_region"]

    client = boto3.client(service_name="secretsmanager", region_name=region_name)

    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secrets = json.loads(get_secret_value_response["SecretString"])
    api_key = secrets["api_key"]

    return api_key


def get_page(api_key, username, page_number=1, from_uts=0, to_uts=10000000000, limit=200):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "format": "json",
        "username": username,
        "api_key": api_key,
        "limit": limit,
        "page": page_number,
        "from": from_uts,
        "to": to_uts,
    }

    request = requests.PreparedRequest()
    request.prepare_url(url, params)

    logger.info(f"Requesting: {request.url.replace(api_key, 'REDACTED_API_KEY')}")

    response = requests.get(request.url)

    if response.status_code != 200:
        logger.error(f"Non-200 Status: {response.status_code}")

    response_json = response.json()

    if "error" in response_json:
        logger.error(f"Error {response['error']}: {response['message']}")

    return response_json


def scrobbles_to_csv_string(page, artist_replacements, album_replacements, track_replacements):
    # string that the CSV writer can write to like a file
    csv_string = io.StringIO()

    writer = csv.writer(csv_string, quoting=csv.QUOTE_NONNUMERIC)

    for scrobble in page["recenttracks"]["track"]:
        # skip currently playing tracks
        if "@attr" in scrobble and scrobble["@attr"]["nowplaying"] == "true":
            continue

        artist_name = scrobble["artist"]["#text"]
        for original, replacement in artist_replacements.items():
            artist_name = artist_name.replace(original, replacement)
        artist_name = artist_name.strip()

        album_name = scrobble["album"]["#text"]
        for original, replacement in album_replacements.items():
            album_name = album_name.replace(original, replacement)
        album_name = album_name.strip()

        track_name = scrobble["name"]
        for original, replacement in track_replacements.items():
            track_name = track_name.replace(original, replacement)
        track_name = track_name.strip()

        unix_timestamp = int(scrobble["date"]["uts"])

        # response includes 4 sizes of album art for each scrobble, use the largest (300x300)
        album_art_url = ""
        for image in scrobble["image"]:
            if image["size"] == "extralarge":
                album_art_url = image["#text"]

        csv_row = [track_name, album_name, artist_name, unix_timestamp, album_art_url]
        writer.writerow(csv_row)

    return csv_string.getvalue()
