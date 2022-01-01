import tweepy
import time
from datetime import timezone
import datetime
import os

print(tweepy.__version__)
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_key = os.getenv("ACCESS_KEY")
access_secret = os.getenv("ACCESS_SECRET")
print(consumer_key)
print(consumer_secret)
print(access_key)
print(access_secret)
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth, timeout=5)

wait_time = 120


# TODO: use tweepy rate-limit status
def utc_timestamp():
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    return int(round(utc_time.timestamp()))


def fetch_last_id():
    for post in api.user_timeline(count=1):
        return post.id


def should_reply(tweet):
    # do not reply to self
    if tweet.author is not None and tweet.author.id == 1468237925057974295:
        return False

    text = tweet.text.lower()
    if 'capitalocene' in text or 'capitalocène' in text or 'miss' in text or 'reviewed' in text:
        return False
    # do not reply to music album "miss anthropocene"
    if 'miss' in text:
        return False
    if 'anthropocene' in text or 'anthropocène' in text:
        return True
    return False


def reply_job(since_id):
    print("searching tweets since : ", since_id, flush=True)
    last_tweet_id = since_id

    try:
        for tweet in api.search_tweets(q="anthropocene -filter:retweets",
                                       count=20,
                                       result_type="recent",
                                       since_id=last_tweet_id):
            print("reply scanning tweet", flush=True)
            if should_reply(tweet):
                print("should reply to some tweet", flush=True)
                if tweet.lang == "fr":
                    print("replying in french", flush=True)
                    api.update_status("*capitalocène",
                                      in_reply_to_status_id=tweet.id,
                                      auto_populate_reply_metadata=True)
                    last_tweet_id = tweet.id
                    continue
                else:
                    print("replying in english", flush=True)
                    api.update_status("*capitalocene",
                                      in_reply_to_status_id=tweet.id,
                                      auto_populate_reply_metadata=True)
                    last_tweet_id = tweet.id
                    continue
    except Exception as e:
        print(e)
        if "too many requests" in str(e).lower():
            reset = int(e.response.headers.get("x-rate-limit-reset"))
            now = utc_timestamp()
            sleep_time = reset - now + 10
            print("rate limit reached in reply job -- sleeping for " +
                  str(sleep_time) + " seconds",
                  flush=True)
            time.sleep(sleep_time)
        elif "status is a duplicate" in str(e).lower():
            print("duplicate ? -- increment last id")
            last_tweet_id = fetch_last_id()
        else:
            print("exception -- keep running", flush=True)

    return last_tweet_id


def reply_to_mention(text, reply_to_id):
    print("reply in french to a mention", flush=True)
    api.update_status(text,
                      in_reply_to_status_id=reply_to_id,
                      auto_populate_reply_metadata=True)


def mention_job(since_id):
    print("searching mentions since: ", since_id, flush=True)
    last_tweet_id = since_id

    try:
        for tweet in api.mentions_timeline(since_id=last_tweet_id):
            reply_to_id = tweet.id
            if reply_to_id is not None:
                text = tweet.text.lower()
                if 'explain' in text or 'explique' in text:
                    if tweet.lang == "fr":
                        print("reply in french to a mention", flush=True)
                        reply_to_mention(
                            "Bien sûr. L'anthropocène est un concept fallacieux faisant porter la responsabilité sur les humains considérés sans distinction, faisant oublier les structures économiques dans lesquelles ils évoluent. Le capitalocène pointe la responsabilité du capitalisme et des capitalistes.",
                            reply_to_id)
                        last_tweet_id = reply_to_id
                        continue
                    else:
                        print("reply in english to a mention", flush=True)
                        reply_to_mention(
                            "Sure. The Anthropocene is a fallacious concept placing responsibility on humans considered without distinction, making us forget the economic structures in which they evolve. The capitalocene points to the responsibility of capitalism and capitalists.",
                            reply_to_id)
                        last_tweet_id = reply_to_id
                        continue

                if "elaborate" in text or "précise" in text or "precise" in text:
                    if tweet.lang == "fr":
                        print("reply in french to a mention", flush=True)
                        reply_to_mention(
                            "Bien sûr. Le capitalisme et les capitalistes sont seuls responsables de la destruction de l'écosystème. Ils feront tout pour nous le faire oublier afin de conserver leurs rentes basées sur l'exploitation de la nature et des travailleurs.",
                            reply_to_id,
                        )
                        last_tweet_id = reply_to_id
                        continue
                    else:
                        print("reply in english to a mention", flush=True)
                        reply_to_mention(
                            "Sure. Capitalism and capitalists are solely responsible for the destruction of the ecosystem. They will do everything to make us forget it in order to preserve their rents based on the exploitation of nature and workers.",
                            reply_to_id)
                        last_tweet_id = reply_to_id
                        continue

                if "thank you" in text or "merci" in text or "good bot" in text or "gentil bot" in text:
                    if tweet.lang == "fr":
                        print("reply in french to a mention", flush=True)
                        reply_to_mention(
                            "Je vous en prie. Tout le plaisir est pour moi",
                            reply_to_id,
                        )
                        last_tweet_id = reply_to_id
                        continue
                    else:
                        print("reply in english to a mention", flush=True)
                        reply_to_mention("You're very welcome. My pleasure!",
                                         reply_to_id)
                        last_tweet_id = reply_to_id
                        continue
    except Exception as e:
        print(e)
        if "too many requests" in str(e).lower():
            reset = int(e.response.headers.get("x-rate-limit-reset"))
            now = utc_timestamp()
            sleep_time = reset - now + 10
            print("rate limit reached in mention job -- sleeping for " +
                  str(sleep_time) + " seconds",
                  flush=True)
            time.sleep(sleep_time)
        elif "status is a duplicate" in str(e).lower():
            print("duplicate ? -- increment last id")
            last_tweet_id = fetch_last_id()
        else:
            print("exception -- keep running", flush=True)
    return last_tweet_id


last_id_reply = fetch_last_id()
last_id_mention = last_id_reply

while True:
    try:
        last_id_reply = reply_job(last_id_reply)
        last_id_mention = mention_job(last_id_mention)
        print("loop done -- sleep " + str(wait_time) + " secs", flush=True)
        time.sleep(wait_time)
    except Exception as e:
        print(e)
        print("expection in main-- sleep " + str(wait_time) +
              " secs and continue",
              flush=True)
        time.sleep(wait_time)
        continue
