import logging
import azure.functions as func
from ..common import api, table


def get_url_from_tweet_data(max_tweet_id):
    return 'https://twitter.com/qwer/status/{}'.format(max_tweet_id)


def get_most_replied_to_str(most_replied_to_user, most_replied_to_times):
    if not most_replied_to_user:
        return ''
    
    user_metrics = api.get_user_public_metrics(most_replied_to_user)
    username = user_metrics['data']['username']
    msg_str = 'User you replied the most to ({} times) is @{}\n'.format(most_replied_to_times, username)
    return msg_str


def serialize_stats_to_msg(tweet_stats):
    max_tweet_id = tweet_stats['MaxTweetId']
    total_like_count = tweet_stats['TotalLikeCount']
    total_reply_count = tweet_stats['TotalReplyCount']
    num_of_tweets = tweet_stats['NumOfTweets']

    ratio = round(total_like_count*1.0/num_of_tweets, 2)
    max_tweet_url = get_url_from_tweet_data(max_tweet_id)

    most_replied_to = get_most_replied_to_str(tweet_stats['MostRepliedToUser'], tweet_stats['MostRepliedToTimes'])
    msg_str = 'You tweeted {} times so far, and received {} likes and {} replies, in total.\n' \
    '{}' \
    'Your like/tweet ratio is {}, and your most popular tweet was:\n{}' \
    .format(num_of_tweets, total_like_count, total_reply_count, most_replied_to, ratio, max_tweet_url)

    logging.info('Message length: {}'.format(len(msg_str)))
    logging.info(msg_str)

    return msg_str


def get_twitter_stats_from_table(tweet_id, user_id):
    users_table = table.UsersTable()
    user_stats = users_table.get_stats_for_user(tweet_id, user_id)
    return user_stats


def mark_user_as_completed(user_id):
    pass # TODO


def post_results_for_user(tweet_id, user_id, comment_id):
    tweet_stats = get_twitter_stats_from_table(tweet_id, user_id)
    msg_str = serialize_stats_to_msg(tweet_stats)
    # TODO
    # api.post_comment(comment_id, msg_str)
    # mark_user_as_completed(user_id)


def main(msg: func.QueueMessage) -> None:
    msg_content = msg.get_body().decode('utf-8')
    logging.info('Python queue trigger function processed a queue item: %s', msg_content)
    tweet_id, user_id, comment_id = msg_content.split('|')

    post_results_for_user(tweet_id, user_id, comment_id)
