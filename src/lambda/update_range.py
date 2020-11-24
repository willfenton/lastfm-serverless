import logging
import lastfm
import s3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    from_uts = event["from_uts"]
    to_uts = event["to_uts"]

    s3_bucket = os.environ["data_bucket"]
    api_key = lastfm.get_api_key()

    if "pages" in event:
        pages = event["pages"]
        for page_number in pages:
            page = lastfm.get_page_from_to(api_key, page_number, from_uts, to_uts)
            page_csv = lastfm.page_to_csv_string(page)
            s3_key = f"scrobbles/{from_uts}-{to_uts}-{page_number}.csv"
            s3.write_string_to_s3(s3_bucket, s3_key, page_csv)
    else:
        first_page = lastfm.get_page_from_to(api_key, 1, from_uts, to_uts)
        page_csv = lastfm.page_to_csv_string(first_page)
        s3_key = f"scrobbles/{from_uts}-{to_uts}-1.csv"
        s3.write_string_to_s3(s3_bucket, s3_key, page_csv)

        total_pages = int(first_page["recenttracks"]["@attr"]["totalPages"])

        if total_pages > 1:
            for page_number in range(2, total_pages + 1):
                page = lastfm.get_page_from_to(api_key, page_number, from_uts, to_uts)
                page_csv = lastfm.page_to_csv_string(page)
                s3_key = f"scrobbles/{from_uts}-{to_uts}-{page_number}.csv"
                s3.write_string_to_s3(s3_bucket, s3_key, page_csv)

    return {"key": "value"}
