import json
import boto3
from botocore.exceptions import ClientError
import logging
import requests
import os


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
