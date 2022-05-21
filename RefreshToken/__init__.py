import datetime
import logging

import azure.functions as func
from ..common import api, table

def refresh_token():
    token_table = table.OauthTokenTable()
    current_token = token_table.get_current_token()
    new_token = api.get_new_oauth_token(current_token)
    token_table.set_new_token(new_token)


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    refresh_token()