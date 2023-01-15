import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import tkinter as tk


def action():
    date_parse = e.get().split('/')
    date_parse = f'{date_parse[2]}-{date_parse[1]}-{date_parse[0]}'
    print(date_parse)
    function(date_parse)


# ##### UI #####
window = tk.Tk()
window.config(width=200, height=200, bg='#20322e')

e = tk.Entry(width=30)
e.insert(tk.END, 'aaaa-mm-aa')
e.pack()

button = tk.Button(text="Build playlist", command=action)
button.pack()

label = tk.Label(text='')
label.pack()

SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')


def function(selected_date):
    playlist_id = ''
    response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{selected_date}")
    response.raise_for_status()
    data = response.text
    soup = BeautifulSoup(data, 'html.parser')
    title = soup.select(selector="li h3", class_="c-title")
    song_list = []
    for n in title:
        if str(n.string) != 'None':
            song_list.append(str(n.string).split('\n\n\t\n\t\n\t\t\n\t\t\t\t\t')[1].split('\t\t\n\t\n')[0])

    date = selected_date.split("-")
    year = date[0]
    # Spotify Authentication
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri="http://localhost:8000",
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            show_dialog=True,
            cache_path="token.txt"
        )
    )
    user_id = sp.current_user()["id"]

    # Searching Spotify for songs by title
    song_uris = []
    year = selected_date.split("-")[0]
    for song in song_list[0:11]:
        result = sp.search(q=f"track:{song} year:{year}", type="track")
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")

    # Creating a new private playlist in Spotify
    playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)

    # Adding songs found into the new playlist
    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
    deliver(playlist["id"])


def deliver(playlist):
    final = f'https://open.spotify.com/playlist/{playlist}'
    print(final)


window.mainloop()
