import json
import os


# Get the JSON configuration file.
file_path = os.path.normpath("{0}/config.json".format(
    os.path.dirname(os.path.realpath(__file__))
))

# Read the config and setup the settings dictionary
with open(file_path, 'r') as file:
    config = json.loads(file.read())

# Main Settings
BOT_TOKEN = config["main"]["bot_token"]

# Welcome Message Channels
CHANNEL_ID_LOBBY = config["welcome"]["lobby"]
CHANNEL_ID_INFO = config["welcome"]["info"]
CHANNEL_ID_UPDATES = config["welcome"]["updates"]

# Twitter Settings
CONSUMER_KEY = config["twitter"]["consumer_key"]
CONSUMER_SECRET = config["twitter"]["consumer_secret"]
OAUTH_TOKEN = config["twitter"]["auth"]["access_token"]
OAUTH_TOKEN_SECRET = config["twitter"]["auth"]["access_token_secret"]
TWEET_WATCHING = config["twitter"]["watching"]
TWEET_CHANNEL_ID = config["twitter"]["tweet_channel_id"]

# Allowed Pin Channels
ALLOWED_PIN_CHANNELS = config["channel_pin"]["channel_ids"]
