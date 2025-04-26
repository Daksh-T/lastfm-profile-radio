# Last.fm Profile Radio

Last.fm Profile Radio is a Flask web app that let's you play a last.fm user's scrobbled tracks as a radio.

## Features

- Fetch and display 25 unique tracks from Last.fm for configurable time periods (last week, last month, past 6 months, this year, past year).
- Play any track on YouTube or open a playlist of selected tracks directly in YouTube.

## Prerequisites

- Python 3
- Last.fm API Key (set in `.env` as `LASTFM_API_KEY`)

## Installation

1. Clone the repository:
   ```shell
   git clone https://github.com/Daksh-T/lastfm-profile-radio.git
   cd lastfm-profile-radio
   ```
2. Install dependencies:
   ```shell
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Last.fm API key:
   ```env
   LASTFM_API_KEY=your_lastfm_api_key_here
   ```

## Usage

1. Start the Flask app:
   ```shell
   python app.py
   ```
2. Open your browser and navigate to `http://localhost:5000/`.
3. Enter a Last.fm username and select a time period.
4. Click **Load Tracks** to load the tracks.
5. Use the **Play on YouTube** buttons to open individual videos or **Open as playlist on YouTube** to launch as a playlist.

## Configuration

- Environment variable `LASTFM_API_KEY` is required for accessing the Last.fm API.
- Adjust the sampling size or periods in `app.py` as needed.