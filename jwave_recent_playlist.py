import tweepy
import streamlit as st
from datetime import datetime, timedelta, timezone
import requests
import json
import re
import base64

# Twitter API credentials
twitterAPIKey = st.secrets["twitterAPIKey"]
twitterAPIKeySecret = st.secrets["twitterAPIKeySecret"]
twitterAccessToken = st.secrets["twitterAccessToken"]
twitterAccessTokenSecret = st.secrets["twitterAccessTokenSecret"]

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(twitterAPIKey, twitterAPIKeySecret)
auth.set_access_token(twitterAccessToken, twitterAccessTokenSecret)

# Create API object
api = tweepy.API(auth)

# Set time range for tweets to retrieve
JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
since_time = now - timedelta(hours=24)

# Retrieve tweets from J-wave account
tweets = tweepy.Cursor(api.user_timeline,
                       screen_name="jwave",
                       tweet_mode="extended",
                       since_id=since_time.timestamp(),
                       include_rts=False).items()

# iTunes Store API endpoint
ITUNES_API = "https://itunes.apple.com/search"

# Define function to search iTunes Store
def itunes_search(q):
    try:
        params = {
            "term": q.replace(" ", "+"),
            "media": "music",
            "entity": "song",
            "limit": 1
        }
        response = requests.get(ITUNES_API, params=params)
        data = json.loads(response.text)
        if data.get("resultCount", 0) > 0:
            return data["results"][0]["trackViewUrl"]
        else:
            return ""
    except json.JSONDecodeError:
        return ""

# Display title and time range
st.title("J-wave 24hrs recent playlist")
st.write(f"({since_time.strftime('%m/%d %H:%M')}〜{now.strftime('%m/%d %H:%M')})")

# Process tweets and display playlist
for tweet in tweets:
    # Check if tweet is within the desired time range
    tweet_time = tweet.created_at.astimezone(JST)
    if tweet_time < since_time:
        break

    # Extract song information from tweet
    match = re.match(r'「(.+)」\s+(.+)\s+(\d{2}:\d{2})', tweet.full_text)
    if match:
        title, artist, timestamp = match.groups()

        # Search for song on iTunes Store
        itunes_link = itunes_search(title + " " + artist)

        # Build YouTube search query
        youtube_query = title + " " + artist + " official video"
        youtube_query = youtube_query.replace(" ", "+")
        youtube_link = f"https://www.youtube.com/results?search_query={youtube_query}&force_navigate=1"

        # Build Spotify search query
        spotify_query = title + " " + artist
        spotify_query = spotify_query.replace(" ", "+")
        spotify_link = f"https://open.spotify.com/search/{spotify_query}"

        # Display song information and links
        st.write(f'{title} / {artist} ({timestamp}) ', unsafe_allow_html=True)
        if itunes_link:
            itunes_png = base64.b64encode(open('its.png', 'rb').read()).decode('utf-8')
            st.write(f'<a href="{itunes_link}" target="_blank"><img src="data:image/png;base64,{itunes_png}" width="20" height="20"></a>', unsafe_allow_html=True)
        if youtube_link:
            youtube_png = base64.b64encode(open('youtube.png', 'rb').read()).decode('utf-8')
            st.write(f'<a href="{youtube_link}" target="_blank"><img src="data:image/png;base64,{youtube_png}" width="20" height="20"></a>', unsafe_allow_html=True)
        if spotify_link:
            spotify_png = base64.b64encode(open('spotify.png', 'rb').read()).decode('utf-8')
            st.write(f'<a href="{spotify_link}" target="_blank"><img src="data:image/png;base64,{spotify_png}" width="20" height="20"></a>', unsafe_allow_html=True)
