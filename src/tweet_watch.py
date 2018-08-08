import discord
from discord.ext import commands
import peony
import peony.oauth_dance
from peony.exceptions import Unauthorized
from datetime import datetime
from .utils import config
import json
import os

DATA_STORE = os.path.normpath("{0}/../tweet_watch_data.json".format(
    os.path.dirname(os.path.realpath(__file__))
))


def is_retweet(data):
    return 'retweeted_status' in data


def is_status_reply(data):
    """
    Whether this is a reply to a status. True if either a watched user
    replied to a status or if a watched user's status was replied to.
    """
    return data["in_reply_to_status_id_str"] is not None


class TweetWatch:
    config = {}
    client = None
    tweet_stream = None

    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(config.CHANNEL_ID_TWITTER)

        self.reload_config()

    def __unload(self):
        if self.tweet_stream is not None:
            self.tweet_stream.cancel()

    def reload_config(self):
        try:
            with open(DATA_STORE, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError as e:
            self.create_fresh_config()

        if 'auth' in self.config:
            self.setup_twitter_client()
            self.listen_for_tweets()

    def save_config(self):
        with open(DATA_STORE, 'w+') as f:
            f.truncate(0)
            f.seek(0)
            json.dump(self.config, f)

    def create_fresh_config(self):
        self.config = {"watches": []}
        self.save_config()

    def watch_account(self, account, last_tweet=None):
        pass

    @commands.command(pass_context=True)
    @commands.has_role("admins!!!")
    async def twitter_setup(self, ctx):
        """Starts the preparation of the Twitter listener."""
        sender = ctx.message.author

        auth_url_prefix = "https://api.twitter.com/oauth/authorize?oauth_token="
        token = await peony.oauth_dance.get_oauth_token(config.CONSUMER_KEY, config.CONSUMER_SECRET)

        dm_auth = """
To monitor Twitter feeds, I need to be authorized on behalf of someone's account on Twitter. \
To use an account you have access to, follow this link and authorize: {url}. I won't use your \
account for any other purpose, and cannot tweet, retweet, follow, DM or make any other changes \
to your account.
        """.format(url=auth_url_prefix + token['oauth_token'])
        dm_followup = """
Once authorized, you will receive a PIN code to complete authorization. Send me the PIN in \
__this__ DM window to complete setup. If you don't enter a PIN in the next 3 minutes, I'll assume you \
no longer want to authorize me with Twitter. You can also say 'cancel' at any time to stop.
        """

        dms = await self.bot.send_message(sender, dm_auth)
        await self.bot.send_message(sender, dm_followup)

        await self.bot.say("{user}: I've sent you instructions in a DM to set up Twitter feed monitoring.".format(user=sender.mention))

        while True:
            message = await self.bot.wait_for_message(author=ctx.message.author, channel=dms.channel, timeout=180)

            if message is None:
                dm_timeout = "Just to let you know: you didn't send your PIN in time, so I'm cancelling the setup."
                await self.bot.send_message(sender, dm_timeout)
                return
            elif message.content.strip().lower() == 'cancel':
                dm_cancel = "Okay, I'm cancelling the setup."
                await self.bot.send_message(sender, dm_cancel)
                return

            try:
                token = await peony.oauth_dance.get_access_token(
                    config.CONSUMER_KEY,
                    config.CONSUMER_SECRET,
                    oauth_verifier=message.content.strip(),
                    **token
                )
            except Unauthorized:
                dm_cancel = "That PIN didn't work, double check and try again. You can say 'cancel' to stop."
                await self.bot.send_message(sender, dm_cancel)
                continue

            break

        self.config["auth"] = dict(
            access_token=token['oauth_token'],
            access_token_secret=token['oauth_token_secret']
        )

        self.save_config()

        dm_success = "You have successfully authenticated and Twitter functionality is now ready."
        await self.bot.send_message(sender, dm_success)

    @commands.command()
    @commands.has_role("admins!!!")
    async def twitter_watch(self, ctx, account):
        pass

    @commands.command()
    @commands.has_role("admins!!!")
    async def twitter_stop(self):
        result = self.cancel_listen_for_tweets()
        if result:
            await self.bot.say("Okay, I'll stop posting tweets as they happen.")
        else:
            await self.bot.say("I can't stop posting tweets as I'm already not posting.")

    @commands.command()
    @commands.has_role("admins!!!")
    async def twitter_start(self):
        if self.client is None:
            await self.bot.say("I can't start posting tweets as I'm not fully set up yet.")
        elif self.tweet_stream is not None:
            await self.bot.say("I'm already posting tweets.")
        else:
            self.listen_for_tweets()
            await self.bot.say("Okay, I'm now listening for tweets to post.")

    def is_user_reply(self, data, count_from_watchers=True):
        """
        Whether this is a reply to a user (@-tweet). True if either a watched user
        @'s someone or if a watched user as @'ed at.

        The optional `count_from_watchers` parameter will exclude @'s made _by_
        watched users.
        """
        if count_from_watchers:
            return data["in_reply_to_user_id_str"] is not None
        else:
            return data["in_reply_to_user_id_str"] is not None \
                and not data["user"]["id_str"] in self.config['watches']

    async def get_tweet_stream(self):
        if self.client is not None:
            async with self.client.stream.statuses.filter.post(follow=",".join(self.config['watches'])) as stream:
                async for data in stream:
                    if peony.events.on_connect(data):
                        print("Listening for tweets.")
                    elif peony.events.on_tweet(data):
                        try:
                            if is_retweet(data) or is_status_reply(data) or \
                              self.is_user_reply(data, count_from_watchers=False):
                                continue
                            tweet = discord.Embed(
                                type='rich',
                                timestamp=datetime.fromtimestamp(int(data['timestamp_ms']) / 1000),
                                colour=int(data['user']['profile_background_color'], 16),
                                url='https://twitter.com/{user}/status/{tweet_id}'.format(user=data['user']['screen_name'], tweet_id=data['id_str']),
                                description=data.text
                            )

                            tweet.set_author(name='{name} (@{user})'.format(name=data['user']['screen_name'], user=data['user']['screen_name']),
                                             url='https://twitter.com/{user}'.format(user=data['user']['screen_name']),
                                             icon_url=data['user']['profile_image_url_https'])

                            tweet.set_footer(text='Twitter',
                                             icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png",
                                             )

                            await self.bot.send_message(self.bot.get_channel(config.CHANNEL_ID_TWITTER),
                                                        content='https://twitter.com/{user}/status/{tweet_id}'
                                                        .format(user=data['user']['screen_name'], tweet_id=data['id_str']))
                        except Exception as e:
                            print("Couldn't write out tweet", repr(e))

    def setup_twitter_client(self):
        self.client = peony.PeonyClient(
            consumer_key=config.CONSUMER_KEY,
            consumer_secret=config.CONSUMER_SECRET,
            **self.config['auth'])

    def listen_for_tweets(self):
        if self.client is None:
            return

        if self.tweet_stream is not None:
            self.tweet_stream.cancel()
        self.tweet_stream = discord.compat.create_task(self.get_tweet_stream(), loop=self.bot.loop)

    def cancel_listen_for_tweets(self):
        if self.tweet_stream is None:
            return False

        self.tweet_stream.cancel()
        self.tweet_stream = None
        return True


def setup(bot):
    bot.add_cog(TweetWatch(bot))
