import logging
import lastfm


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def test_handler(event, context):
    api_key = lastfm.get_api_key()
    page = lastfm.get_page(api_key, 1)

    return page
