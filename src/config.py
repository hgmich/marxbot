import sqlite3
import json
import os

# Point to DB and Config File
INFO_DB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'info.db')
CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')


# Load Config File
with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)


# Connect to SQLite DB
def db_connect(db_path=INFO_DB):
    con = sqlite3.connect(db_path)
    return con


# Setup Connection and Cursor for Most Stuff
conn = db_connect()
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get Config Stuff Part 1
channels = cur.execute("SELECT * FROM channels").fetchone()
roles = cur.execute("SELECT * FROM roles").fetchone()
counting_config = cur.execute("SELECT * FROM counting").fetchone()

# Cleanup
cur.close()
conn.close()

# Setup Connection and Cursor for Pin Channels
conn = db_connect()
conn.row_factory = lambda cursor, row: row[0]
cur = conn.cursor()

# Get Pin Channels
pin_channels = cur.execute("SELECT channel_id FROM pin_channels").fetchall()

# Cleanup
cur.close()
conn.close()

# Main Settings
BOT_TOKEN = config["bot_token"]

# CHANNEL IDS
CHANNEL_ID_BOT = channels["bot"]
CHANNEL_ID_CLIPBOARD = channels["clipboard"]
CHANNEL_ID_COUNTING = channels["counting"]
CHANNEL_ID_GENERAL = channels["general"]
CHANNEL_ID_INFO = channels["info"]
CHANNEL_ID_JOINLEAVE = channels["joinleave"]
CHANNEL_ID_LOBBY = channels["lobby"]
CHANNEL_ID_TWITTER = channels["twitter"]
CHANNEL_ID_UPDATES = channels["updates"]
CHANNEL_ID_WELCOME = channels["welcome"]

# ROLE IDS
ROLE_ID_ADMIN = roles["admin"]
ROLE_ID_MOD = roles["mod"]
ROLE_ID_MEMBER = roles["member"]
ROLE_ID_DEFAULT = roles["default"]

# COUNTING
CURRENT_COUNT = counting_config["current"]
RECORD_COUNT = counting_config["record"]

# TWITTER SETTINGS
CONSUMER_KEY = config["twitter_consumer_key"]
CONSUMER_SECRET = config["twitter_consumer_secret"]

# Allowed Pin Channels
ALLOWED_PIN_CHANNELS = pin_channels


# Update Counting
def update_counting():
    con = db_connect()
    c = con.cursor()

    if CURRENT_COUNT > RECORD_COUNT:
        sql = "UPDATE counting SET current = " + str(CURRENT_COUNT) + ", record = " + str(CURRENT_COUNT) + " WHERE id = 1"
    else:
        sql = "UPDATE counting SET current = " + str(CURRENT_COUNT) + " WHERE id = 1"

    try:
        c.execute(sql)
        con.commit()
        return True
    except:
        return False


# Check for Clipboard
def on_clipboard(message_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "SELECT COUNT(*) FROM clipboard WHERE message_id = ?"
    c.execute(sql, (message_id,))
    data = c.fetchone()[0]

    c.close()
    con.close()

    return data != 0


# Add message to clipboard
def add_clipboard(message_id: str, clipped_id: str, reacts: int = 5):
    con = db_connect()
    c = con.cursor()

    sql = "INSERT INTO clipboard (message_id, clipped_id, total_clips) VALUES (?, ?, ?)"

    try:
        c.execute(sql, (message_id, clipped_id, reacts))
        con.commit()
        return True
    except:
        return False


# Increase Clip Count
def increase_clip(message_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "UPDATE clipboard SET total_clips = (total_clips + 1) WHERE message_id = ?"

    try:
        c.execute(sql, (message_id,))
        con.commit()
        return True
    except:
        return False


# Decrease Clip Count
def decrease_clip(message_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "UPDATE clipboard SET total_clips = (total_clips - 1) WHERE message_id = ?"

    try:
        c.execute(sql, (message_id,))
        con.commit()
        return True
    except:
        return False


# Add Member to "No Clip" List
def add_noclip_member(member_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "REPLACE INTO no_clip_members (member_id) VALUES (?)"

    try:
        c.execute(sql, (member_id,))
        con.commit()
        return True
    except:
        return False


# Remove Member from "No Clip" List
def remove_noclip_member(member_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "DELETE FROM no_clip_members WHERE member_id = ?"

    try:
        c.execute(sql, (member_id,))
        con.commit()
        return True
    except:
        return False


# Get "No Clip" Members
def get_noclip_members():
    con = db_connect()
    con.row_factory = lambda cursor, row: row[0]
    c = con.cursor()

    sql = "SELECT member_id FROM no_clip_members"

    try:
        c.execute(sql)
        return c.fetchall()
    except:
        return []


# Add Info to Profile
def update_profile_info(member_id: str, field: str, data: str):
    con = db_connect()
    c = con.cursor()

    sql = "REPLACE INTO profiles (?) VALUES (?) WHERE user_id = ?"

    try:
        c.execute(sql, (field, data, member_id))
        con.commit()
        return True
    except:
        return False


# Get Profile Info
def get_field_users(field: str):
    con = db_connect()
    c = con.cursor()

    sql = "SELECT member_id, ? FROM profiles WHERE member_id IS NOT NULL AND ? IS NOT NULL"

    try:
        c.execute(sql, (field, field))
        return c.fetchall()
    except:
        return []
