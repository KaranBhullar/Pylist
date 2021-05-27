from pathlib import Path
from googleapiclient.discovery import build
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sys
import re

scope = 'playlist-modify-public';
client_id = ENV_PYLIST_CLIENT_ID;
client_secret = ENV_PYLIST_SECRET_ID;
redirect_path = 'http://localhost:3000/';
track_id = '';
song_list = '';
sp = '';
yt_key = ENV_PYLIST_YOUTUBE_KEY;

def user_verification():
    global username;
    global token;
    global sp;
    username = input("Enter your spotify username: ");
    print("%s" %(username));
    print('Online..\n');

    try: #Attempts creating authentication token
        token = spotipy.util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_path);
    except:#if cancel is pressed 
        print("You must accept to use the program");
        sys.exit(0);
    sp = spotipy.Spotify(token);

def addTrack(song_list):
    for song in song_list:
        lineLst = song.split(',');
        try:
            lineLst[0] = lineLst[0].strip(); #Song
            lineLst[1] = lineLst[1].strip(); #Artist
            lineLst[2] = lineLst[2].strip(); #playlist
        except:
            print("The file is formatted incorrectly.");
            sys.exit(0);
        
        searchPlaylist(lineLst[0],lineLst[1],lineLst[2]);

def searchPlaylist(song, artist, playlist_name):
    user_playlists = sp.user_playlists(username)['items'];
    for playlist in user_playlists:
        
        if (playlist['name'] == playlist_name): #checks if playlist already exists
            playlist_id = playlist['id'];
            searchTrack(artist,song, playlist_id);
            break     
    else:
        new_playlist = sp.user_playlist_create(username, playlist_name, True, "Created using the SpotiPy API");
        user_playlists.insert(0,new_playlist);
        playlist_id = new_playlist['id'];
        searchTrack(artist, song, playlist_id);
        print("Playlist Created.\n");

def searchTrack(artist, track, playlist_id):
    global track_id;
    global sp;
    try:
        results = sp.search("artist:"+artist+" track:"+track)['tracks']['items'];
        track_id = results[0]['id'];
        sp.user_playlist_add_tracks(username,playlist_id,[track_id]);
    except:
        print('A song could not be found. Either the song/artist is not on spotify or there is a typo in the read file.');
        return;

def addToSpotify(song_list):
    with open('readthis.txt', 'r') as f:
        song_list = f.read().split('\n');        
    song_list = list(filter(None, song_list));
    user_verification();
    addTrack(song_list);

def youtube(video):
    user_verification();
    pg_token = None;
    global song_list;
    youtube = build('youtube','v3',developerKey=yt_key);
    
    try:
        yt_playlist_id = re.findall("list=(.+?)&", video) or re.findall("list=(.+?)$", video);
    except:
        print("Invalid video URL. Make sure the video is in a playlist");
        
    print(yt_playlist_id[0]);
    while pg_token != 1234: #flag for when no more pages
        yt_playlist = youtube.playlistItems().list(part="snippet", playlistId=yt_playlist_id[0], maxResults=50, pageToken=pg_token);
        yt_playlist_name = youtube.playlists().list(part="snippet", id=yt_playlist_id[0]).execute();
        yt_playlist_info = yt_playlist.execute() or None;
       
        for song in yt_playlist_info['items']:
            title = re.sub("\([^)]*\)", "", song['snippet']['title']);
            title = re.sub("\[(.+?)\]", "", title);
            title = re.sub("\*(.+?)\*", "", title);
            title = title.replace(" ft.", "");
            title = title.replace(" feat.", "-");
            title = title.replace("'","");
            title = title.replace('"', "- ");
            title = title.replace('–', "- ");
            title = title.replace("|", "-");
            title = title.split("- ");
            try:
                title.remove('');
            except: None
            print(title);
            try:
                searchPlaylist(title[1],title[0],yt_playlist_name['items'][0]['snippet']['title']);
            except:
                print("Song is not the correct format 'Artist - Song' or 'Artist | Song'");
        try:
            pg_token = yt_playlist_info['nextPageToken'];
        except:
            pg_token = 1234;
     
        
if(__name__ == "__main__"):
    print("1. Upload to Spotify.");
    print("2. Import from Youtube.");
    print("3. Export playlist from Spotify.");
    choice = input("Enter a number (1 2 or 3):  ");
    
    if(choice == '1'): addToSpotify(song_list)
    elif(choice == '2'): 
        video = input("Enter a youtube link: ");
        youtube(video);
    elif(choice == '3'): print("Unavailable as of right now.");
    else: print("Invalid input");
    