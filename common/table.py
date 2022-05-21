from abc import ABC
from collections import UserString
from datetime import datetime
from distutils.dep_util import newer
import os
from azure.data.tables import TableClient, UpdateMode
from enum import Enum


connection_string = os.environ['QueueConnectionString']


class Table(ABC):
    def __init__(self, table_name) -> None:
        super().__init__()
        self.table_client = TableClient.from_connection_string(connection_string, table_name)


class TrackedTweetsTable(Table):
    TRACKED_TWEETS_TABLE_NAME = 'TrackedTweets'

    def __init__(self) -> None:
        super().__init__(self.TRACKED_TWEETS_TABLE_NAME)

    def read_tracked_tweets_from_table(self):
        query_filter = '' # Read all documents
        tracked_tweets = self.table_client.query_entities(query_filter)
        return [(tweet['PartitionKey'], tweet['RowKey'], tweet['SinceId']) for tweet in tracked_tweets]

    def update_newest_id(self, tweet_id, author_id, newest_id):
        doc = {
            'PartitionKey': str(tweet_id),
            'RowKey': str(author_id),
            'SinceId': str(newest_id),
            'ModifiedDate': datetime.utcnow()
        }
        self.table_client.upsert_entity(mode=UpdateMode.MERGE, entity=doc)


class UsersTable(Table):
    USERS_TABLE_NAME = 'CommentingUsers'

    class UserState(Enum):
        InProgress = 1
        StatsAdded = 2
        Completed = 3

    def __init__(self) -> None:
        super().__init__(self.USERS_TABLE_NAME)

    def get_preexisting_commenting_users(self, tweet_id):
        query_filter = 'PartitionKey eq \'{}\''.format(tweet_id)
        entities = self.table_client.query_entities(query_filter)
        return set([entity['RowKey'] for entity in entities])

    def get_stats_for_user(self, tweet_id, user_id):
        entity = self.table_client.get_entity(tweet_id, user_id)
        return entity

    def update_new_comment_for_processing(self, tweet_id, user_id, comment_id):
        doc = {
            'PartitionKey': str(tweet_id),
            'RowKey': str(user_id),
            'CommentId': str(comment_id),
            'State': self.UserState.InProgress,
            'ModifiedDate': datetime.utcnow()
        }
        self.table_client.upsert_entity(mode=UpdateMode.MERGE, entity=doc)

    def update_twitter_stats_for_user(self, tweet_id, user_id, comment_id, tweet_stats):
        max_tweet_id, total_like_count, total_reply_count, total_retweet_count, total_quote_count, num_of_tweets, most_replied_to = tweet_stats
        doc = {
            'PartitionKey': str(tweet_id),
            'RowKey': str(user_id),
            'CommentId': str(comment_id),
            'MaxTweetId': max_tweet_id,
            'TotalLikeCount':total_like_count,
            'TotalReplyCount':total_reply_count,
            'TotalRetweetCount':total_retweet_count,
            'TotalQuoteCount':total_quote_count,
            'NumOfTweets':num_of_tweets,
            'MostRepliedToUser':most_replied_to[0] if most_replied_to else None,
            'MostRepliedToTimes':most_replied_to[1] if most_replied_to else None,
            'State': self.UserState.StatsAdded,
            'ModifiedDate': datetime.utcnow()
        }
        self.table_client.upsert_entity(mode=UpdateMode.MERGE, entity=doc)

class OauthTokenTable(Table):

    OAUTH_TOKEN_TABLE_NAME = 'OauthToken'
    PARTITION_KEY = 'TokenPartition'
    ROW_KEY = 'TokenRow'

    def __init__(self) -> None:
        super().__init__(self.OAUTH_TOKEN_TABLE_NAME)

    def get_current_token(self):
        entity = self.table_client.get_entity(self.PARTITION_KEY, self.ROW_KEY)
        return entity['Value']

    def set_new_token(self, new_token):
        doc = {
            'PartitionKey': self.PARTITION_KEY,
            'RowKey': self.ROW_KEY,
            'Value': new_token,
            'ModifiedDate': datetime.utcnow()
        }
        self.table_client.upsert_entity(mode=UpdateMode.MERGE, entity=doc)
