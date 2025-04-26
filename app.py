import os
import time
import datetime
from flask import Flask, render_template, request, jsonify, redirect
import requests
from dotenv import load_dotenv
from youtubesearchpython import VideosSearch
import random

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('LASTFM_API_KEY')
API_URL = 'http://ws.audioscrobbler.com/2.0/'


def get_recent_tracks(username, from_ts=None, to_ts=None):
    """Fetch recent tracks for a Last.fm user within an optional time range."""
    params = {
        'method': 'user.getrecenttracks',
        'user': username,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 100,
    }
    if from_ts:
        params['from'] = from_ts
    if to_ts:
        params['to'] = to_ts

    response = requests.get(API_URL, params=params)
    data = response.json()
    return data.get('recenttracks', {}).get('track', [])


def get_all_tracks(username, from_ts=None, to_ts=None):
    """Fetch a sample of recent tracks in one request."""
    params = {
        'method': 'user.getrecenttracks',
        'user': username,
        'api_key': API_KEY,
        'format': 'json',
        'limit': 200,
        'page': 1,
    }
    if from_ts: params['from'] = from_ts
    if to_ts:   params['to'] = to_ts
    resp = requests.get(API_URL, params=params)
    data = resp.json().get('recenttracks', {})
    # return list of track dicts
    return data.get('track', [])


def get_user_profile_image(username):
    """Retrieve Last.fm user profile image URL."""
    params = {
        'method': 'user.getinfo',
        'user': username,
        'api_key': API_KEY,
        'format': 'json'
    }
    try:
        r = requests.get(API_URL, params=params, timeout=5)
        data = r.json()
        images = data.get('user', {}).get('image', [])
        # pick largest non-empty image
        for img in reversed(images):
            url = img.get('#text')
            if url:
                return url
    except Exception:
        pass
    return ''


@app.route('/', methods=['GET', 'POST'])
def index():
    tracks = []
    username = ''
    profile_image = ''
    # define periods
    periods = ['last_week','last_month','past_6_months','this_year','past_year']
    period = 'this_year'  # default

    if request.method == 'POST':
        username = request.form.get('username')
        profile_image = get_user_profile_image(username)
        period = request.form.get('period') or period
        # compute timestamps based on period
        now = datetime.datetime.now()
        if period == 'last_week':
            start_dt = now - datetime.timedelta(days=7)
        elif period == 'last_month':
            start_dt = now - datetime.timedelta(days=30)
        elif period == 'past_6_months':
            start_dt = now - datetime.timedelta(days=182)
        elif period == 'past_year':
            start_dt = now - datetime.timedelta(days=365)
        else:  # this_year
            start_dt = datetime.datetime(now.year, 1, 1)
        from_ts = int(time.mktime(start_dt.timetuple()))
        to_ts = int(time.mktime(now.timetuple()))

        # fetch up to first 5 pages (~500 scrobbles) then sample
        fetched = get_all_tracks(username, from_ts, to_ts)
        seen = set()
        uniq = []
        for t in fetched:
            key = (t['name'], t['artist']['#text'])
            if key not in seen:
                seen.add(key)
                uniq.append(t)
        # sample up to 25
        tracks = random.sample(uniq, min(len(uniq), 25)) if uniq else []
    
    # render with the selected period
    return render_template('index.html', tracks=tracks, username=username, period=period, profile_image=profile_image)


@app.route('/<username>')
def user_radio(username):
    """Auto-load last month's radio for the given username via URL path."""
    # fetch profile image
    profile_image = get_user_profile_image(username)
    # period = last month
    now = datetime.datetime.now()
    start_dt = now - datetime.timedelta(days=30)
    from_ts = int(time.mktime(start_dt.timetuple()))
    to_ts = int(time.mktime(now.timetuple()))
    # fetch and dedupe
    fetched = get_all_tracks(username, from_ts, to_ts)
    seen = set()
    uniq = []
    for t in fetched:
        key = (t['name'], t['artist']['#text'])
        if key not in seen:
            seen.add(key)
            uniq.append(t)
    # sample up to 25
    tracks = random.sample(uniq, min(len(uniq), 25)) if uniq else []
    # render same template
    return render_template('index.html', tracks=tracks, username=username, period='last_month', profile_image=profile_image)


@app.route('/video_id')
def get_video_id():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'id': ''})
    vid = ''
    try:
        videosSearch = VideosSearch(q, limit=1)
        res = videosSearch.result()
        vid = res.get('result', [{}])[0].get('id', '')
    except TypeError:
        # handle underlying httpx proxies error
        pass
    except Exception:
        # any other errors
        pass
    # fallback: scrape YouTube search HTML for videoId
    if not vid:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            resp = requests.get('https://www.youtube.com/results', params={'search_query': q}, headers=headers, timeout=5)
            import re
            match = re.search(r'"videoId":"([^"]+)"', resp.text)
            if match:
                vid = match.group(1)
        except Exception:
            pass
    return jsonify({'id': vid})


if __name__ == '__main__':
    app.run(debug=True)
