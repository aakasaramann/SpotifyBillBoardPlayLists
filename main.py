from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import os

SPOTIPY_CLIENT_ID = os.environ['client_id']
SPOTIPY_CLIENT_SECRET = os.environ['client_secret']
SPOTIFY_SCOPE = 'playlist-modify-private'
REDIRECT_URI = 'http://example.com'

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get("https://www.billboard.com/charts/hot-100/" + date)

soup = BeautifulSoup(response.text, 'html.parser')
song_names_tags = soup.find_all("h3", class_="a-no-trucate")
song_names = [song.getText().replace('\n', '').replace('\t', '') for song in song_names_tags]
artist_names_spans = soup.find_all("span", class_="a-no-trucate")
artist_names = [artist.getText().replace('\n', '').replace('\t', '') for artist in artist_names_spans]

chart_list = [{'Song': song_names[i], 'Artist': artist_names[i]} for i in range(len(song_names))]

pprint(chart_list)

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        scope=SPOTIFY_SCOPE,
        redirect_uri=REDIRECT_URI,
        show_dialog=True,
        cache_path="token.txt"
    ))
user_id = sp.current_user()["id"]

song_uris = []
for i in chart_list:
    result = sp.search(q=f"track:{i['Song']} artist:{i['Artist'].replace('Featuring','').replace('&','')}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{i['Song']} by {i['Artist']} doesn't exist in Spotify. Skipped.")

pprint(song_uris)

playlist = sp.user_playlist_create(user=user_id, name=f'{date} Billboard Top 100', public=False, collaborative=False, description='')

print(playlist['id'])

sp.playlist_add_items(playlist_id=playlist['id'], items=song_uris)
