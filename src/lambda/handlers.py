import logging
import lastfm
import s3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_handler(event, context):
    lb = event["start"]
    ub = event["end"]
    s3_bucket = os.environ["data_bucket"]
    api_key = lastfm.get_api_key()
    for page_number in range(lb, ub):
        page = lastfm.get_page(api_key, page_number)
        page_csv = lastfm.page_to_csv_string(page)
        s3.write_string_to_s3(s3_bucket, f"scrobbles/{page_number}.csv", page_csv)

    return {"key": "value"}
