import tweepy
from tweepy.auth import OAuthHandler
from common.utils import getTwitterCreds


class TwitterAPI:
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            twitter_creds = getTwitterCreds()
            if not all(twitter_creds.values()):
                # improve error handling
                raise ValueError("Missing one or more Twitter API credentials")
            cls._instance = super().__new__(cls)
            #create v2 endpoint
            cls._instance.client = tweepy.Client(**twitter_creds)
            # Create v1.1 API
            auth = OAuthHandler(
                twitter_creds.get("consumer_key"),
                twitter_creds.get("consumer_secret")
            )
            auth.set_access_token(
                twitter_creds.get("access_token"),
                twitter_creds.get("access_token_secret")
            )
            cls._instance.api = tweepy.API(auth)
        return cls._instance
    
    @staticmethod
    def getClient():
        return TwitterAPI()._instance.client

    @staticmethod
    def getApi():
        return TwitterAPI()._instance.api
    
    