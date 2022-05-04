from datetime import datetime
from distutils.dep_util import newer
import os
from azure.data.tables import TableClient, UpdateMode
from enum import Enum


TABLE_URL = 'https://twitterstatsrga0df.table.core.windows.net/CommentingUsers'
TABLE_NAME = 'CommentingUsers'
USERS_PARTITION_KEY = 'users'
TRACKED_TWEETS_PARTITION_KEY = 'tracked_tweets'

class UserState(Enum):
    New = 1
    InProgress = 2
    Completed = 3

connection_string = os.getenv('CONNECTION_STRING')
table_client = TableClient.from_connection_string(connection_string, TABLE_NAME)


def get_preexisting_commenting_users_from_table():
    query_filter = 'PartitionKey eq \'{}\' and (State eq \'{}\' or State eq \'{}\')' \
        .format(USERS_PARTITION_KEY, UserState.Completed, UserState.InProgress)
    entities = table_client.query_entities(query_filter)
    return [entity['RowKey'] for entity in entities]


def update_new_comment_for_processing(user_id):
    doc = {
        'PartitionKey': USERS_PARTITION_KEY,
        'RowKey': str(user_id),
        'State': UserState.InProgress,
        'ModifiedDate': datetime.utcnow()
    }
    table_client.upsert_entity(mode=UpdateMode.MERGE, entity=doc)


def read_tracked_tweets_from_table():
    query_filter = 'PartitionKey eq \'{}\''.format(TRACKED_TWEETS_PARTITION_KEY)
    tracked_tweets = table_client.query_entities(query_filter)
    return [(tweet['RowKey'], tweet['AuthorId'], tweet['SinceId']) for tweet in tracked_tweets]


def update_newest_id(tweet_id, author_id, newest_id):
    doc = {
        'PartitionKey': TRACKED_TWEETS_PARTITION_KEY,
        'RowKey': str(tweet_id),
        'AuthorId': str(author_id),
        'SinceId': str(newest_id),
        'ModifiedDate': datetime.utcnow()
    }
    table_client.upsert_entity(mode=UpdateMode.MERGE, entity=doc)
