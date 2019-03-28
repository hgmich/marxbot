import sqlite3
import json
import os
import datetime

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

# Get Pin Channels and No Stat Channels
pin_channels = cur.execute("SELECT channel_id FROM pin_channels").fetchall()
no_stat_channels = cur.execute("SELECT channel_id FROM no_stat_channels").fetchall()

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

# PUNITIVE ROLES
ROLE_ID_NO_EVENTS = roles["no_events"]

# COUNTING
CURRENT_COUNT = counting_config["current"]
RECORD_COUNT = counting_config["record"]

# TWITTER SETTINGS
CONSUMER_KEY = config["twitter_consumer_key"]
CONSUMER_SECRET = config["twitter_consumer_secret"]

# Allowed Pin Channels
ALLOWED_PIN_CHANNELS = pin_channels

# No Stats Channels
NO_STATS_CHANNELS = no_stat_channels

# GAME ROSTER SETTINGS
ALLOWED_GAME_SYSTEMS = ['bnet', 'epic', 'origin', 'psn', 'steam', 'switch', 'uplay', 'xbl']


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


# Add Role to Role List
def add_joinable_role(role_id: str, role_name: str, role_type: str):
    con = db_connect()
    c = con.cursor()

    sql = "REPLACE INTO joinable_roles (id, name, name_lower, type) VALUES (?, ?, ?, ?)"

    try:
        c.execute(sql, (role_id, role_name, role_name.lower(), role_type))
        con.commit()
        return True
    except:
        return False


# Remove Role from Role List
def remove_joinable_role(role_name: str):
    con = db_connect()
    c = con.cursor()

    sql = "DELETE FROM joinable_roles WHERE name = ?"

    try:
        c.execute(sql, (role_name,))
        con.commit()
        return True
    except:
        return False


# Get Roles of Specific Type
def get_roles_by_type(role_type: str):
    con = db_connect()
    con.row_factory = lambda cursor, row: row[0]
    c = con.cursor()

    sql = "SELECT name FROM joinable_roles WHERE type = ? ORDER BY name ASC"

    # Get Roles
    type_roles = c.execute(sql, (role_type,)).fetchall()

    # Cleanup
    c.close()
    con.close()

    return type_roles


# Get Role ID from Role Name Lowercase
def get_role_id_from_lowername(name_lower: str):
    con = db_connect()
    c = con.cursor()

    pattern = "%" + name_lower + "%"

    sql = "SELECT id FROM joinable_roles WHERE name_lower LIKE ?"

    try:
        c.execute(sql, (pattern,))
        rows = c.fetchall()
        count = len(rows)

        if count == 1:
            return rows[0][0]
        elif count > 1:
            return "many"
        else:
            return None
    except:
        return None


# Get Role ID from Role Name Lowercase
def get_role_name_from_id(role_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "SELECT name FROM joinable_roles WHERE id = ?"

    try:
        c.execute(sql, (role_id,))
        row = c.fetchone()
        return row[0]
    except:
        return None


# Add/Edit Game Profile Info
def update_game_profile(member_id: str, game_system: str, game_id: str):
    con = db_connect()
    c = con.cursor()

    sql1 = "INSERT OR IGNORE INTO game_profile (discord_id, " + game_system + ") VALUES (?, ?)"
    sql2 = "UPDATE game_profile SET " + game_system + " = '" + game_id + "' WHERE discord_id = " + member_id

    try:
        c.execute(sql1, (member_id, game_id))
        c.execute(sql2)
        con.commit()
        return True
    except:
        return False


# Remove Game Profile Info
def remove_game_profile(member_id: str, game_system: str):
    con = db_connect()
    c = con.cursor()

    sql = "UPDATE game_profile SET " + game_system + " = NULL WHERE discord_id = " + member_id

    try:
        c.execute(sql)
        con.commit()
        return True
    except:
        return False


# Delete All Game Profile Info
def delete_game_profile(member_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "DELETE FROM game_profile WHERE discord_id = " + member_id

    try:
        c.execute(sql)
        con.commit()
        return True
    except:
        return False


# Get Game Profiles of Specific System
def get_game_profiles_by_system(game_system: str):
    con = db_connect()
    con.row_factory = sqlite3.Row
    c = con.cursor()

    sql = "SELECT discord_id, " + game_system + " FROM game_profile WHERE " + game_system + " IS NOT NULL"

    # Get Profiles
    profiles = c.execute(sql).fetchall()

    # Cleanup
    c.close()
    con.close()

    return profiles


# Add Role to Event Role List
def add_event_role(role_id: str, role_name: str, creator_id: str, date_created: str):
    con = db_connect()
    c = con.cursor()

    sql = "INSERT INTO event_roles (role_id, role_name, creator_id, date_created) VALUES (?, ?, ?, ?)"

    try:
        c.execute(sql, (role_id, role_name, creator_id, date_created))
        con.commit()
        return True
    except:
        return False


# Remove Role from Event Role List
def remove_event_role(role_id: str):
    con = db_connect()
    c = con.cursor()

    sql = "DELETE FROM event_roles WHERE role_id = ?"

    try:
        c.execute(sql, (role_id,))
        con.commit()
        return True
    except:
        return False


# Get List of Event Roles
def get_event_roles():
    con = db_connect()
    con.row_factory = lambda cursor, row: row[0]
    c = con.cursor()

    sql = "SELECT role_name FROM event_roles"

    # Get Roles
    roles = c.execute(sql).fetchall()

    # Cleanup
    c.close()
    con.close()

    return roles


# Get Event Role Info from Name
def get_event_role_info(role_name: str):
    con = db_connect()
    con.row_factory = sqlite3.Row
    c = con.cursor()

    pattern = "%" + role_name.lower() + "%"

    sql = "SELECT * FROM event_roles WHERE LOWER(role_name) LIKE ?"

    try:
        c.execute(sql, (pattern,))
        rows = c.fetchall()
        count = len(rows)

        if count == 1:
            return rows[0]
        elif count > 1:
            return "many"
        else:
            return None
    except:
        return None


# Add Event to Event Calendar
def add_event_calendar(member_id: str, event_date: str, event_description: str):
    con = db_connect()
    c = con.cursor()

    sql = "INSERT INTO event_calendar (event_date, planner_id, description) VALUES (?, ?, ?)"

    try:
        c.execute(sql, (event_date, member_id, event_description))
        con.commit()
        return True
    except:
        return False


# Update Event in the Event Calendar
def update_event_calendar(event_id: int, event_date: str, event_description: str):
    con = db_connect()
    c = con.cursor()

    sql = "UPDATE event_calendar SET event_date = ?, description = ? WHERE event_id = ?"

    try:
        c.execute(sql, (event_date, event_description, event_id))
        con.commit()
        return True
    except:
        return False


# Remove Event from Event Calendar
def remove_event_calendar(event_id: int):
    con = db_connect()
    c = con.cursor()

    sql = "DELETE FROM event_calendar WHERE event_id = ?"

    try:
        c.execute(sql, (event_id,))
        con.commit()
        return True
    except:
        return False


# Get Specific Event from Calendar by Event ID
def get_calendar_event(event_id: int):
    con = db_connect()
    con.row_factory = sqlite3.Row
    c = con.cursor()

    sql = "SELECT * FROM event_calendar WHERE event_id = ?"

    try:
        c.execute(sql, (event_id,))
        row = c.fetchone()
        return row
    except:
        return None


# Get Events In Calendar
def get_events_in_calendar():
    con = db_connect()
    con.row_factory = sqlite3.Row
    c = con.cursor()

    # Set Date
    today = datetime.date.today().strftime('%Y-%m-%d')

    sql = "SELECT * FROM event_calendar WHERE event_date >= ? ORDER BY event_date LIMIT 25"

    # Get Profiles
    events = c.execute(sql, (today,)).fetchall()

    # Cleanup
    c.close()
    con.close()

    return events


# Purge Old Event Information (Roles and Calendar)
def clean_events():
    con = db_connect()
    c = con.cursor()

    # Set Dates
    today = datetime.date.today().strftime('%Y-%m-%d')
    two_weeks_ago = (datetime.date.today() - datetime.timedelta(days=14)).strftime('%Y-%m-%d')

    sql_roles = "DELETE FROM event_roles WHERE date_created < ?"
    sql_calendar = "DELETE FROM event_calendar WHERE event_date < ?"

    try:
        c.execute(sql_roles, (two_weeks_ago,))
        c.execute(sql_calendar, (today,))
        con.commit()
        return True
    except:
        return False
