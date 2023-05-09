import os
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import matplotlib.pyplot as plt
from sklearn import decomposition

import streamlit as st

# ---*--- Streamlit WebApp Header ---*---
st.header('Spotify Streamlit WebApp Tutorial Demo')

range_choices = ['Top 50', 'Top 69', 'Top 100']
range_selected = st.sidebar.selectbox("Your Top n songs choice please: ", range_choices)

button_clicked = st.button("Start Clustering")

if range_selected == 'Top 50':
    n = 50
elif range_selected == 'Top 69':
    n = 69
elif range_selected == 'Top 100':
    n = 100

os.environ['SPOTIPY_CLIENT_ID'] = 'e12c85ea786949cdb7d9df050b6f8f88'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'add4eb11b00a40d9a01a2908586d70c7'
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://localhost:8080'

scope = "user-library-read"

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = spotify.current_user_saved_tracks()

tracks = results['items']
while results['next']:
    results = spotify.next(results)
    tracks.extend(results['items'])

liked_songs_uris = []
liked_songs_df = pd.DataFrame(columns=["track_name", "added_date",
                                       "track_release_date", "track_popularity",
                                       "af_danceability", "af_energy", "af_key",
                                       "af_loudness", "af_mode", "af_speechiness",
                                       "af_acousticness", "af_instrumentalness",
                                       "af_liveness", "af_valence", "af_tempo", "af_type",
                                       "af_duration", "af_time_signature", "main_artist_uri",
                                       "main_artist_name", "main_artist_followers",
                                       "main_artist_genres", "main_artist_popularity"])

# ---*--- Fetch Top Songs ---*---

if button_clicked:

    for idx, item in enumerate(tracks[:n]):
        track = item['track']
        track_uri = track["uri"]

        liked_songs_uris.append(track_uri)

        liked_songs_df.loc[track_uri, "added_date"] = item["added_at"]
        liked_songs_df.loc[track_uri, "track_name"] = track["name"]
        liked_songs_df.loc[track_uri, "track_release_date"] = track["album"]["release_date"]
        liked_songs_df.loc[track_uri, "track_popularity"] = track["popularity"]

        audio_features = spotify.audio_features([track_uri])[0] #function requires a list

        liked_songs_df.loc[track_uri, "af_danceability"] = audio_features["danceability"]
        liked_songs_df.loc[track_uri, "af_energy"] = audio_features["energy"]
        liked_songs_df.loc[track_uri, "af_key"] = audio_features["key"]
        liked_songs_df.loc[track_uri, "af_loudness"] = audio_features["loudness"]
        liked_songs_df.loc[track_uri, "af_mode"] = audio_features["mode"]
        liked_songs_df.loc[track_uri, "af_speechiness"] = audio_features["speechiness"]
        liked_songs_df.loc[track_uri, "af_acousticness"] = audio_features["acousticness"]
        liked_songs_df.loc[track_uri, "af_instrumentalness"] = audio_features["instrumentalness"]
        liked_songs_df.loc[track_uri, "af_liveness"] = audio_features["liveness"]
        liked_songs_df.loc[track_uri, "af_valence"] = audio_features["valence"]
        liked_songs_df.loc[track_uri, "af_tempo"] = audio_features["tempo"]
        liked_songs_df.loc[track_uri, "af_type"] = audio_features["type"]
        liked_songs_df.loc[track_uri, "af_duration"] = audio_features["duration_ms"]
        liked_songs_df.loc[track_uri, "af_time_signature"] = audio_features["time_signature"]

        main_artist_uri = track["artists"][0]["uri"]
        liked_songs_df.loc[track_uri, "main_artist_uri"] = main_artist_uri
        main_artist = spotify.artist(main_artist_uri)
        liked_songs_df.loc[track_uri, "main_artist_name"] = main_artist["name"]
        liked_songs_df.loc[track_uri, "main_artist_followers"] = main_artist["followers"]["total"]
        liked_songs_df.loc[track_uri, "main_artist_genres"] = main_artist["genres"]
        liked_songs_df.loc[track_uri, "main_artist_popularity"] = main_artist["popularity"]


    # ---*--- Start Clustering ---*---

    np.random.seed(42)

    #select number of clusters
    n_clust = 5

    # import the songs, project only some of the features.
    #songs_ori = pd.read_pickle("liked_songs.pkl")
    songs_ori = liked_songs_df
    features = ["af_danceability", "af_energy","af_acousticness","af_instrumentalness","af_valence"]
    songs = songs_ori.loc[:,features]


    # # normalize loudness
    # songs["af_loudness"] = -songs["af_loudness"]
    # songs["af_loudness"] = [round((i - min(songs["af_loudness"])) / (max(songs["af_loudness"])
    #                             - min(songs["af_loudness"])), 3) for i in songs["af_loudness"]]


    #do a PCA
    pca = decomposition.PCA(n_components=2)
    pca.fit(songs)
    songs_PCA = pca.transform(songs)
    print("PCA metrics")
    print(pca.explained_variance_ratio_)
    print(pca.singular_values_)
    print(pca.components_)


    #cluster the songs
    from sklearn.cluster import KMeans
    kmeans_model = KMeans(n_clusters=n_clust, random_state=1).fit(songs)
    labels = kmeans_model.labels_

    #plot the songs with their labels in a PCA
    fig, ax = plt.subplots()
    plt.scatter(songs_PCA[:,0], songs_PCA[:,1], alpha = 0.3, c=labels)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    st.pyplot(fig)