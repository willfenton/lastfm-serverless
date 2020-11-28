import logging
import math
import os

import lastfm
import s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(event)

    from_uts = event["from_uts"]
    to_uts = event["to_uts"]
    lastfm_username = event["lastfm_username"]

    s3_bucket = os.environ["data_bucket"]
    api_key = lastfm.get_api_key()

    result = {"num_pages": 0, "s3_objects_written": []}

    # get specific pages in the time range
    # {
    #     "from_uts": 1606114800,
    #     "to_uts": 1606201199,
    #     "pages": [1, 2, 3, 4, 5, 6]
    # }
    if "pages" in event:
        pages = event["pages"]

    # get all pages in the time range
    # {
    #     "from_uts": 1606114800,
    #     "to_uts": 1606201199
    # }
    else:
        page = lastfm.get_page(api_key, lastfm_username, from_uts=from_uts, to_uts=to_uts, limit=1)
        num_scrobbles = int(page["recenttracks"]["@attr"]["total"])
        num_pages = math.ceil(num_scrobbles / 200)
        pages = list(range(1, num_pages + 1))

    for page_number in pages:
        page = lastfm.get_page(api_key, lastfm_username, page_number, from_uts, to_uts)
        csv = lastfm.scrobbles_to_csv_string(page)
        s3_key = f"{lastfm_username}/scrobbles/{from_uts}-{to_uts}-{page_number}.csv"
        s3.write_string_to_s3(s3_bucket, s3_key, csv)

        result["num_pages"] += 1
        result["s3_objects_written"].append(s3_key)

    logger.info(result)

    return result
