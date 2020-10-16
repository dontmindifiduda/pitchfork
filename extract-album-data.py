#!/usr/bin/env python
# coding: utf-8

import sqlite3, datetime
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import requests
import string
import time
import re
import os

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MultiLabelBinarizer

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 

from bs4 import BeautifulSoup



con = sqlite3.connect('database.sqlite')
scores = pd.read_sql('SELECT reviewid, artist, title, score, author FROM reviews', con)
genres = pd.read_sql('SELECT reviewid, genre FROM genres', con)
con.close()


# Preprocessing & Cleaning
# One Hot Encode Genres


genres['genre'] = genres['genre'].fillna('unknown')
genres['genre'].value_counts()

le = LabelEncoder()
genres['genre'] = le.fit_transform(genres['genre'])

genres_grouped = genres.groupby(['reviewid'])['genre'].apply(list).reset_index()
genres_grouped['genre'] = genres_grouped['genre'].apply(tuple)
genres_grouped['genre'] = [tuple(value) for value in genres_grouped['genre']]


mlb = MultiLabelBinarizer()
genres_ohe = mlb.fit_transform(genres_grouped['genre'].values.tolist())

genre_ohe_df = pd.DataFrame(genres_ohe, columns = le.classes_)
genre_ohe_df['reviewid'] = genres_grouped['reviewid'].values
genre_cols = ['reviewid', 'electronic', 'experimental', 'folk/country', 'global', 'jazz',
              'metal', 'pop/r&b', 'rap', 'rock', 'unknown']
genre_ohe_df = genre_ohe_df[genre_cols]


# Identify Top and Bottom 10% of Albums Based on Score
# Sort by ranking and extract the top and bottom 10% (1839) albums 
top_albums = scores.sort_values(by='score', ascending=False)[:1840].reset_index(drop=True)
bottom_albums = scores.sort_values(by='score', ascending=False)[-1839:].reset_index(drop=True)


# Clean Album and Artist Names

def clean_name(name):
    name = name.lower()
    name = re.sub('ö', 'o', name)
    name = re.sub(r'\([^)]*\)', '', name).strip()
    name = re.sub("[\(\[].*?[\)\]]", "", name).strip()
    name = re.sub(' & ', ' and ', name)
    name = re.sub('-', ' ', name)
    name = re.sub("[,.']", '', name)
    name = re.sub(' +', ' ', name)
    name = re.sub('"', '', name)
    name = re.sub('!', '', name)
    name = re.sub(':', '', name)
    name = re.sub('/', ' ', name)
    name = re.sub(r'[^0-9A-Za-z ]', '', name)
    name = name.strip()
    
    if name[-3:] == ' ep':
        name = name[:-3]
        
    if name[-4:] == ' ost':
        name = name[:-4]
        
    return name


top_albums['artist'] = top_albums['artist'].apply(clean_name)
top_albums['title'] = top_albums['title'].apply(clean_name)

bottom_albums['artist'] = bottom_albums['artist'].apply(clean_name)
bottom_albums['title'] = bottom_albums['title'].apply(clean_name)


# Clean up album names from review database

top_albums.loc[(top_albums['artist'] == 'the velvet underground') & 
               (top_albums['title'] == 'the velvet underground  45th anniversary super deluxe edition'), 
               'title'] = 'the velvet underground'

top_albums.loc[(top_albums['artist'] == 'roots manuva') &
               (top_albums['title'] == 'brand new secondhand'), 
               'title'] = 'brand new second hand'

top_albums.loc[(top_albums['artist'] == 'guided by voices') &
               (top_albums['title'] == 'human amusement at hourly rates: the best of guided by voices'), 
               'title'] = 'human amusements at hourly rates the best of guided by voices'

top_albums.loc[top_albums['title'] == 'tropiclia: a brazilian revolution in sound', 
               'title'] = 'tropicalia a brazilian revolution in sound'

top_albums.loc[top_albums['title'] == 'tigerbeat6 inc', 
               'title'] = 'tigerbeat inc disc 1'

top_albums.loc[(top_albums['artist'] == 'sufjan stevens') &
               (top_albums['title'] == 'greetings from michigan'), 
               'title'] = 'michigan'

top_albums.loc[(top_albums['artist'] == 'super furry animals') &
               (top_albums['title'] == 'love kraft'), 
               'title'] = 'lovekraft'

top_albums.loc[(top_albums['artist'] == 'david lang') &
               (top_albums['title'] == 'the little match girl passion'), 
               'title'] = 'lang the little match girl passion'

top_albums.loc[(top_albums['artist'] == 'ziq') &
               (top_albums['title'] == "tango n' vectif"), 
               'title'] = "tango n'vectif"

top_albums.loc[(top_albums['artist'] == 'william onyeabor') &
               (top_albums['title'] == 'who is william onyeabor'), 
               'title'] = 'world psychedelic classics 5 who is william onyeabor'

top_albums.loc[(top_albums['artist'] == 'justice') & 
               (top_albums['title'] == ''),
               'title'] = 'cross'

top_albums.loc[(top_albums['artist'] == 'love is all') & 
               (top_albums['title'] == 'nine times that same song'),
               'title'] = '9 times that same song'

top_albums.loc[top_albums['artist'] == 'prince the revolution',
               'artist'] = 'prince'

top_albums.loc[top_albums['title'] == 'dusk at cubist castle',
               'artist'] = 'the olivia tremor control'

top_albums.loc[top_albums['artist'] == 'sunn o',
               'artist'] = 'sunn 0)))'

top_albums.loc[top_albums['artist'] == 'bjrk',
               'artist'] = 'bjork'

top_albums.loc[top_albums['artist'] == 'sigur rs',
               'artist'] = 'sigur ros'

top_albums.loc[top_albums['artist'] == 'jhann jhannsson',
               'artist'] = 'jóhann jóhannsson'

top_albums.loc[(top_albums['artist'] == 'otis redding') &
               (top_albums['title'] == 'live at the whiskey a go go the complete recordings'),
               'title'] = 'live at the whisky a go go'

top_albums.loc[(top_albums['artist'] == 'half japanese') &
               (top_albums['title'] == 'gentlemen not beasts'),
               'title'] = 'half gentlemen not beasts'

top_albums.loc[(top_albums['artist'] == 'sigur ros') &
               (top_albums['title'] == 'agaetis byrjun'),
               'title'] = 'Ágaetis byrjun'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'london is the place for me part four'),
               'title'] = 'london is the place for me 4'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'black foliage animation music vol 1'),
               'artist'] = 'the olivia tremor control'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'wattstax'),
               'title'] = 'wattstax: the living word'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'music from the unrealized film script dusk at cubist castle'),
               'title'] = 'dusk at cubist castle'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'dusk at cubist castle'),
               'artist'] = 'olivia tremor control'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'de stijl'),
               'artist'] = 'the white stripes'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'nigeria 70 the definitive story of 1970s funky lagos'),
               'title'] = 'nigeria 70 funky lagos'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'methodology 74 78 attic tapes'),
               'artist'] = 'cabaret voltaire'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'shangaan electro new wave dance music from south africa'),
               'title'] = 'new wave dance music from south africa'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'new wave dance music from south africa'),
               'artist'] = 'shangaan electro'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'brazil 70 after tropiclia new directions in brazilian music in the 1970s'),
               'title'] = 'brazil 70 after tropicalia'

top_albums.loc[(top_albums['artist'] == 'morton feldman ives ensemble') &
               (top_albums['title'] == 'string quartet ii'),
               'title'] = 'morton feldman string quartet (ii)'

top_albums.loc[top_albums['artist'] == 'orchestre poly rythmo de cotonou',
               'artist'] = 'tp orchestre poly rythmo'

top_albums.loc[(top_albums['artist'] == 'tp orchestre poly rythmo') &
               (top_albums['title'] == 'volume one the vodoun effect'),
               'title'] = 'the vodoun effect'

top_albums.loc[top_albums['artist'] == 'gyrgy ligeti',
               'artist'] = 'gyorgy ligeti'

top_albums.loc[(top_albums['artist'] == 'gyorgy ligeti') &
               (top_albums['title'] == 'the ligeti project ii'),
               'title'] = 'Ligeti Project Vol.2 - Lontano, Atmosphères, Apparitions, San Francisco Polyphony & Concert Românesc'

top_albums.loc[top_albums['artist'] == 'caf tacuba',
               'artist'] = 'café tacvba'

top_albums.loc[top_albums['artist'] == 'brian eno karl hyde',
               'artist'] = 'eno • hyde'

top_albums.loc[(top_albums['artist'] == 'peter brtzmann william parker hamid drake') &
               (top_albums['title'] == 'never too late but always too early'),
               'title'] = 'peter brotzmann'

top_albums.loc[top_albums['artist'] == 'fantmas',
               'artist'] = 'fantomas'

top_albums.loc[top_albums['artist'] == 'world standard wechsel garland',
               'artist'] = 'world standard'

top_albums.loc[(top_albums['artist'] == 'various artists') &
               (top_albums['title'] == 'young money rise of an empire'),
               'artist'] = 'young money'

top_albums.loc[(top_albums['artist'] == 'young money') &
               (top_albums['title'] == 'young money rise of an empire'),
               'title'] = 'rise of an empire'

top_albums.loc[top_albums['artist'] == 'koenji hyakkei',
               'artist'] = 'koenjihyakkei'

top_albums.loc[top_albums['artist'] == 'the peter brtzmann sextet   quartet',
               'artist'] = 'the peter brotzmann sextet'


top_albums_remove = [
    'matador at 21',
    'run the road',
    'the art of field recording vol 1',
    'rwd magazine mixtape vol 1',
    'now thing',
    'yellow pills',
    'the rise and fall of paramount records volume one',
    'the rise and fall of paramount records volume two',
    'steam kodok 26 a go go ultrarities from the sixties singapore and south east asia underground',
    'the art of field recording vol 2',
    'stones throw 101',
    'give me love songs of the brokenhearted baghdad 1925 1929'
    'stax 50th anniversary',
    'the third unheard connecticut hip hop 1979 1983',
    'japanese independent music',
    'the upsetter selection a lee perry jukebox',
    'this may be my last time singing',
    'john peel a tribute',
    'parallelogram' ,
]


for album in top_albums_remove:
    top_albums = top_albums.loc[top_albums.title != album]
    
top_albums = top_albums.reset_index()



bottom_albums.loc[(bottom_albums['artist'] == 'triangle'), 
                  'title'] = 'star'

bottom_albums.loc[(bottom_albums['artist'] == 'does it offend you, yeah?') &
                  (bottom_albums['title'] == 'you have no idea what you are getting yourself into'), 
                  'title'] = 'you have no idea what youre getting yourself into'

bottom_albums.loc[(bottom_albums['artist'] == 'the moldy peaches') &
                  (bottom_albums['title'] == 'moldy peaches 2000: unreleased cutz and live jamz'), 
                  'title'] = 'unreleased cutz and live jamz'

bottom_albums.loc[(bottom_albums['artist'] == 'ghostland observatory') &
                  (bottom_albums['title'] == 'robotique majestic'), 
                  'title'] = 'robotique majestique'

bottom_albums.loc[(bottom_albums['artist'] == 'mia') &
                  (bottom_albums['title'] == 'y'), 
                  'title'] = '/ \\ / \\ / \\ y / \\'

bottom_albums = bottom_albums.drop(402, axis=0).reset_index(drop=True)

bottom_albums.loc[bottom_albums['artist'] == 'bjrk',
                   'artist'] = 'bjork'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'thumbsucker'), 
                  'artist'] = 'tim delaughter'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'guilt by association'), 
                  'title'] = 'guilt by association digital only bounus version'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'tron legacy reconfigured'), 
                  'artist'] = 'daft punk'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'songs from wonderland'), 
                  'artist'] = 'original cast of wonderland'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'discovered a collection of daft funk samples'), 
                  'title'] = 'daft punk discovered a collection of daft funk samples'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'daft punk discovered a collection of daft funk samples'), 
                  'artist'] = 'daft punk'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'kitsun maison 9'), 
                  'title'] = 'kitsun maison compilation 9 petit bateau edition'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'celebrating the music of inside llewyn davis'), 
                  'title'] = 'inside llewyn davis'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                  (bottom_albums['title'] == 'army of me remixes and covers'), 
                  'artist'] = 'bjork'

bottom_albums.loc[bottom_albums['artist'] == 'charlatans uk',
                   'artist'] = 'the charlatans'

bottom_albums.loc[(bottom_albums['artist'] == 'dave grohl') &
                  (bottom_albums['title'] == 'sound city real to reel'), 
                  'artist'] = 'sound city real to reel'

bottom_albums.loc[(bottom_albums['artist'] == 'the visible men') &
                  (bottom_albums['title'] == 'love 30'), 
                  'title'] = 'Love:30'

bottom_albums.loc[(bottom_albums['artist'] == 'dabrye') &
                  (bottom_albums['title'] == 'two three'), 
                  'title'] = 'Two / Three'

bottom_albums.loc[(bottom_albums['artist'] == 'the hidden cameras') &
                  (bottom_albums['title'] == 'origin orphan'), 
                  'title'] = 'Origin:Orphan'

bottom_albums.loc[(bottom_albums['artist'] == 'the flaming lips stardeath and white dwarfs') &
                  (bottom_albums['title'] == 'the dark side of the moon'), 
                  'title'] = 'The Flaming Lips and Stardeath and White Dwarfs with Henry Rollins and Peaches Doing The Dark Side of the Moon'

bottom_albums.loc[bottom_albums['artist'] == 'beholdthe arctopus',
                   'artist'] = 'behold... the arctopus'

bottom_albums.loc[(bottom_albums['artist'] == 'auteurs') &
                  (bottom_albums['title'] == 'das capital the songwriting genius of luke haines and the auteurs'), 
                  'artist'] = 'luke haines the auteurs'

bottom_albums.loc[(bottom_albums['artist'] == 'luke haines the auteurs') &
                  (bottom_albums['title'] == 'das capital the songwriting genius of luke haines and the auteurs'), 
                  'title'] = 'das capital - the songwriting genius of luke haines and the auteurs'

bottom_albums.loc[(bottom_albums['artist'] == 'cibelle') &
                  (bottom_albums['title'] == 'las vnus resort palace hotel'), 
                  'title'] = 'las venus resort palace hotel'

bottom_albums.loc[(bottom_albums['artist'] == 'british sea power') &
                  (bottom_albums['title'] == 'zeus'), 
                  'title'] = 'zeus ep'

bottom_albums.loc[(bottom_albums['artist'] == 'various artists') &
                   (bottom_albums['title'] == 'young money rise of an empire'),
                   'artist'] = 'young money'

bottom_albums.loc[(bottom_albums['artist'] == 'young money') &
                   (bottom_albums['title'] == 'young money rise of an empire'),
                   'title'] = 'rise of an empire'

bottom_albums.loc[(bottom_albums['artist'] == 'the mars volta') &
                   (bottom_albums['title'] == 'de loused in the comatorium'),
                   'title'] = 'deloused in the comatorium'

bottom_albums.loc[(bottom_albums['artist'] == 'ilya monosov') &
                   (bottom_albums['title'] == 'seven lucky plays or how to fix songs for a broken heart'),
                   'artist'] = 'ilya e. monosov'

bottom_albums.loc[bottom_albums['artist'] == 'takagi masakatsu',
                   'artist'] = 'masakatsu takagi'

bottom_albums.loc[bottom_albums['artist'] == 'steve buscemi elliott sharp',
                   'artist'] = 'steve buscemi & elliott sharp'

bottom_albums.loc[bottom_albums['artist'] == 'sarah lee guthrie johnny irion',
                   'artist'] = 'sarah lee guthrie and johnny irion'

bottom_albums.loc[(bottom_albums['artist'] == 'sarah lee guthrie and johnny irion') &
                   (bottom_albums['title'] == 'wassiac way'),
                   'title'] = 'wassaic way'

bottom_albums.loc[(bottom_albums['artist'] == 'exhaust') &
                   (bottom_albums['title'] == 'enregistraur'),
                   'title'] = 'enregistreur'

bottom_albums.loc[bottom_albums['artist'] == 'mats gustafsson colin stetson',
                   'artist'] = 'colin stetson mats gustafsson'

bottom_albums.loc[bottom_albums['artist'] == 'miss kittin and the hacker',
                   'artist'] = 'miss kittin the hacker'

bottom_albums.loc[(bottom_albums['artist'] == 'electric six') &
                   (bottom_albums['title'] == 'seor smoke'),
                   'title'] = 'senor smoke'

bottom_albums.loc[(bottom_albums['artist'] == 'unkle') &
                   (bottom_albums['title'] == 'end titlesstories for film'),
                   'title'] = 'end titles... stories for film'

bottom_albums.loc[bottom_albums['artist'] == 'jackson and his computerband',
                   'artist'] = 'jackson and his computer band'

bottom_albums.loc[(bottom_albums['artist'] == 'lemon jelly') &
                   (bottom_albums['title'] == 'lemonjellyky'),
                   'title'] = 'lemon jelly.ky'

bottom_albums.loc[(bottom_albums['artist'] == 'earl zinger') &
                   (bottom_albums['title'] == 'put your phazers on stun throw your health food skyward'),
                   'title'] = 'put your phasers on ...'

bottom_albums.loc[(bottom_albums['artist'] == 'stereo image') &
                   (bottom_albums['title'] == 'stereoimage'),
                   'title'] = 's/t'

bottom_albums.loc[(bottom_albums['artist'] == 'adrian orange and her band') &
                   (bottom_albums['title'] == 'adrian orange and her band'),
                   'artist'] = 'adrian orange, her band'

bottom_albums.loc[(bottom_albums['artist'] == 'suntanama') &
                   (bottom_albums['title'] == 'another'),
                   'artist'] = 'the suntanama'

bottom_albums.loc[(bottom_albums['artist'] == 'josh rouse') &
                   (bottom_albums['title'] == 'subttulo'),
                   'title'] = 'subtitulo'

bottom_albums.loc[(bottom_albums['artist'] == 'the peppermints') &
                   (bottom_albums['title'] == 'jess chryst'),
                   'title'] = 'jesus chryst'

bottom_albums.loc[(bottom_albums['artist'] == 'they shoot horses dont they') &
                   (bottom_albums['title'] == 'pick up sticks'),
                   'title'] = 'pickup sticks'

bottom_albums.loc[(bottom_albums['artist'] == 'marky ramone the speedkings') &
                   (bottom_albums['title'] == 'legends bleed'),
                   'artist'] = 'marky ramone and the speedkings'

bottom_albums.loc[(bottom_albums['artist'] == 'youngblood brass band') &
                   (bottom_albums['title'] == 'centerlevelroar'),
                   'artist'] = 'center:level:roar'

bottom_albums.loc[(bottom_albums['artist'] == 'boris ian astbury') &
                   (bottom_albums['title'] == 'bxi'),
                   'artist'] = 'boris & ian astbury'

bottom_albums.loc[(bottom_albums['artist'] == 'liliput kleenex') &
                   (bottom_albums['title'] == 'live recordings tv clips and roadmovie'),
                   'artist'] = 'kleenex/liliput'

bottom_albums.loc[(bottom_albums['artist'] == 'kleenex/liliput') &
                   (bottom_albums['title'] == 'live recordings tv clips and roadmovie'),
                   'title'] = 'live recordings, tv-clips & roadmovie'

bottom_albums.loc[bottom_albums['artist'] == 'kleenexgirlwonder',
                   'artist'] = 'kleenex girl wonder'

bottom_albums.loc[(bottom_albums['artist'] == 'vert') &
                   (bottom_albums['title'] == 'some beans and an octopus'),
                   'artist'] = 'some beans and an octopus, vert'

bottom_albums.loc[bottom_albums['artist'] == 'murder city devils',
                   'artist'] = 'the murder city devils'

bottom_albums.loc[(bottom_albums['artist'] == 'the murder city devils') &
                   (bottom_albums['title'] == 'rip'),
                   'artist'] = 'r.i.p.'

bottom_albums.loc[(bottom_albums['artist'] == 'snoop dogg') &
                   (bottom_albums['title'] == 'rg  the masterpiece'),
                   'title'] = 'r&g (rhythm & gangsta): the masterpiece'

bottom_albums.loc[(bottom_albums['artist'] == 'pixies') &
                   (bottom_albums['title'] == 'ep 2'),
                   'title'] = 'ep2'

bottom_albums.loc[(bottom_albums['artist'] == 'thurston moore') &
                   (bottom_albums['title'] == 'sensitive lethal'),
                   'title'] = 'sensitive/lethal'

bottom_albums.loc[bottom_albums['artist'] == 'muggs',
                   'artist'] = 'dj muggs'

bottom_albums.loc[bottom_albums['artist'] == 's   s   s',
                   'artist'] = 's/s/s'

bottom_albums.loc[(bottom_albums['artist'] == 'architecture in helsinki') &
                   (bottom_albums['title'] == 'now  4eva'),
                   'title'] = 'now + 4eva'


bottom_albums_remove = [
    'woodstock 40 years on back to yasgurs farm',
    'zang tumb tuum the ztt box set',
    'listen to what the man said popular artists pay tribute to paul mccartney',
    'clicks and cuts',
    'to spirit back the mews',
    'definitive jux presents iii',
    'catch the throne the mixtape',
    'rave on a tribute to buddy holly',
    'johnny cash remixed',
    'bbc radio 1 established 1967'
]


for album in bottom_albums_remove:
    bottom_albums = bottom_albums.loc[bottom_albums.title != album]
    
bottom_albums = bottom_albums.reset_index()

playlist_search_albums = [
    'no thanks the 70s punk rebellion',
    'in the beginning there was rhythm',
    'ultimate breaks and beats the complete collection',
    'the very best of ethiopiques hypnotic grooves from the legendary series',
    'the big stiff box set',
    'miami sound rare funk and soul from miami florida 1967 1974',
    'journey into paradise the larry levan story',
    'can you dig it the music and politics of black action films 1968-75',
    'children of nuggets original artyfacts from the second psychedelic era 1976-1996',
    'music from the oc mix 5',
    'american hardcore the history of american punk rock 1980 1986'
]


# Scrape Album Song Data From Spotify
# Import Libraries and Enter Credentials


client_id = 'YOUR_SPOTIFY_CLIENT_ID'
client_secret = 'YOUR_SPOTIFY_CLIENT_SECRET'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)


# Define columns for scraped data

df_columns = ['reviewid', 'artist_name', 'album_title', 'score', 'song_name', 'song_id', 'song_track_number', 
              'song_duration', 'song_explicit', 'song_uri', 'acousticness', 'danceability', 'energy', 'key', 
              'mode', 'time_signature', 'instrumentalness', 'liveness', 'speechiness', 'tempo', 'valence', 
              'popularity', 'release_date']


# Define Helper Functions and Prepare Dataframe for Scraped Data

def check_search_counter(search_counter):
    if search_counter == 4:
        time.sleep(np.random.uniform(2,4))
        return 0
    else:
        return search_counter + 1


def identify_album_matches(album_search_items, album_title, artist_name, search_index, album_list, uri_list):
    
    album_search_result = clean_name(album_search_items[search_index]['name'])
    artist_search_result = clean_name(album_search_items[search_index]['artists'][0]['name'])

    if album_search_result in clean_name(album_title) or clean_name(album_title) in album_search_result:
        if clean_name(artist_name) in artist_search_result or artist_search_result in clean_name(artist_name):
            uri_list.append(album_search_items[search_index]['uri'])
            album_list.append(artist_search_result)
    
    return uri_list, album_list


def identify_playlist_matches(playlist_search_items, playlist_title, artist_name, search_index, album_list, uri_list):
    
    playlist_search_result = clean_name(playlist_search_items[search_index]['name'])

    if playlist_search_result in playlist_title or playlist_title in playlist_search_result:
        uri_list.append(playlist_search_items[search_index]['uri'])
        album_list.append(playlist_search_result)
    
    return uri_list, album_list


def scrape_album_songs(df):
    compiled_df = pd.DataFrame(columns=df_columns)
    missing_album_indices = []
    start_time = time.time()
    search_counter = 0

    for album_index in range(len(df)):
        
        if album_index % 5 == 0:
            print('')
            print('Albums Completed: ', album_index)
            print('Elapsed Time: ', time.time() - start_time)
            print('')

        
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, requests_timeout=60)
                
        reviewid = df.iloc[album_index]['reviewid']
        artist_name = df.iloc[album_index]['artist']
        album_title = df.iloc[album_index]['title']
        score = df.iloc[album_index]['score']
        
        # Search for playlists
        if album_title in playlist_search_albums:
            
            search_results = sp.search(album_title, limit='50', type='playlist')
            playlist_items = search_results['playlists']['items']

            playlist_uris = []
            playlist_names = []

            for playlist_search_index in range(len(playlist_items)):
                playlist_uris, playlist_names = identify_playlist_matches(playlist_items, album_title, artist_name, 
                                                                 playlist_search_index, playlist_names, playlist_uris)

            if len(playlist_uris) == 0:
                print('Album and Playlist Not Found: ', artist_name, ' - ', album_title)
                missing_album_indices.append(album_index)
            else:
                playlist_data = sp.playlist_tracks(playlist_uris[0])

                for song_index in range(len(playlist_data['items'])):
                    song_name = playlist_data['items'][song_index]['track']['name']
                    song_id = playlist_data['items'][song_index]['track']['id']
                    song_track_number = playlist_data['items'][song_index]['track']['track_number']
                    song_duration = playlist_data['items'][song_index]['track']['duration_ms']
                    song_explicit = playlist_data['items'][song_index]['track']['explicit']
                    song_uri = playlist_data['items'][song_index]['track']['uri']

                    track_features = sp.audio_features(song_uri)

                    if track_features != [None]:
                        acousticness = track_features[0]['acousticness']
                        danceability = track_features[0]['danceability']
                        energy = track_features[0]['energy']
                        key = track_features[0]['key']
                        mode = track_features[0]['mode']
                        time_signature = track_features[0]['time_signature']
                        instrumentalness = track_features[0]['instrumentalness']
                        liveness = track_features[0]['liveness']
                        loudness = track_features[0]['loudness']
                        speechiness = track_features[0]['speechiness']
                        tempo = track_features[0]['tempo']
                        valence = track_features[0]['valence']
                        popularity = sp.track(song_uri)['popularity']
                        release_date = sp.track(song_uri)['album']['release_date']


                    new_row = [reviewid, artist_name, album_title, score, song_name, song_id, song_track_number,
                               song_duration, song_explicit, song_uri, acousticness, danceability, energy,
                               key, mode, time_signature, instrumentalness, liveness, speechiness, tempo, 
                               valence, popularity, release_date]

                    compiled_df.loc[len(compiled_df)] = new_row

        
        # Search for albums
        else:
            search_results = sp.search(album_title, limit='50', type='album')
            search_counter = check_search_counter(search_counter)

            # Iterate through album search results and extract album uris that match artist name

            album_uris = []
            album_names = []
            album_items = search_results['albums']['items']

            for album_search_index in range(len(album_items)):

                album_uris, album_names = identify_album_matches(album_items, album_title, artist_name, 
                                                                 album_search_index, album_names, album_uris)

            # If no albums are found, begin searching truncated album names            

            if len(album_uris) == 0 and len(album_title.split(' ')) > 1:
                truncated_album_title = album_title

                while len(truncated_album_title.split(' ')) > 1:
                    truncated_album_title = ' '.join(truncated_album_title.split(' ')[:-1])
                    search_results = sp.search(truncated_album_title, limit='50', type='album')
                    search_counter = check_search_counter(search_counter)
                    album_items = search_results['albums']['items']

                    for album_search_index in range(len(album_items)):
                        album_uris, album_names = identify_album_matches(album_items, truncated_album_title, 
                                                                         artist_name, album_search_index, 
                                                                         album_names, album_uris)

            # If no albums are found after truncated search, attempt to search by artist name

            if len(album_uris) == 0:
                search_results = sp.search(artist_name, limit='50', type='artist')
                search_counter = check_search_counter(search_counter)
                artist_items = search_results['artists']['items']
                artist_uri = None

                for artist_index in range(len(artist_items)):
                    artist_search_result = clean_name(artist_items[artist_index]['name'])
                    if artist_search_result == artist_name:
                        artist_uri = artist_items[artist_index]['uri']
                        break

                if artist_uri != None: 
                    artist_albums = sp.artist_albums(artist_uri, album_type='album')
                    arist_album_items = artist_albums['items']

                    for album_search_index in range(len(arist_album_items)):
                        album_uris, album_names = identify_album_matches(arist_album_items, album_title, 
                                                                         artist_name, album_search_index, 
                                                                         album_names, album_uris)
                        
            # If no albums are found after artist name search, attempt to search by artist name + album name

            if len(album_uris) == 0:
                search_results = sp.search(artist_name + ' ' + album_title, limit='50', type='album')
                search_counter = check_search_counter(search_counter)
                
                album_uris = []
                album_names = []
                album_items = search_results['albums']['items']

                for album_search_index in range(len(album_items)):

                    album_uris, album_names = identify_album_matches(album_items, album_title, artist_name, 
                                                                     album_search_index, album_names, album_uris)

            # If no albums are found after truncated search, flag album as not identified and record index

            if len(album_uris) == 0:
                print('Album Not Found: ', artist_name, ' - ', album_title)
                missing_album_indices.append(album_index)
            else:
                album_data = sp.album_tracks(album_uris[0])

                for song_index in range(len(album_data['items'])):
                    song_name = album_data['items'][song_index]['name']
                    song_id = album_data['items'][song_index]['id']
                    song_track_number = album_data['items'][song_index]['track_number']
                    song_duration = album_data['items'][song_index]['duration_ms']
                    song_explicit = album_data['items'][song_index]['explicit']
                    song_uri = album_data['items'][song_index]['uri']

                    track_features = sp.audio_features(song_uri)

                    if track_features != [None]:
                        acousticness = track_features[0]['acousticness']
                        danceability = track_features[0]['danceability']
                        energy = track_features[0]['energy']
                        key = track_features[0]['key']
                        mode = track_features[0]['mode']
                        time_signature = track_features[0]['time_signature']
                        instrumentalness = track_features[0]['instrumentalness']
                        liveness = track_features[0]['liveness']
                        loudness = track_features[0]['loudness']
                        speechiness = track_features[0]['speechiness']
                        tempo = track_features[0]['tempo']
                        valence = track_features[0]['valence']
                        popularity = sp.track(song_uri)['popularity']
                        release_date = sp.track(song_uri)['album']['release_date']


                    new_row = [reviewid, artist_name, album_title, score, song_name, song_id, song_track_number,
                               song_duration, song_explicit, song_uri, acousticness, danceability, energy,
                               key, mode, time_signature, instrumentalness, liveness, speechiness, tempo, 
                               valence, popularity, release_date]

                    compiled_df.loc[len(compiled_df)] = new_row  
    
    return compiled_df, missing_album_indices


top_album_songs, missing_top_album_indices = scrape_album_songs(top_albums)

print('Found {}% of Top 10% Pitchfork Albums on Spotify'.format(round(100-len(missing_top_album_indices)/1839*100, 2)))


# Scrape Song Info For Bottom 10% of Albums

bottom_album_songs, missing_bottom_album_indices = scrape_album_songs(bottom_albums)

print('Found {}% of Bottom 10% Pitchfork Albums on Spotify'.format(round(100-len(missing_bottom_album_indices)/1839*100, 2)))

integer_conv_cols = ['song_duration', 'song_explicit', 'song_track_number', 'time_signature',
                     'mode', 'key', 'popularity']

for col in integer_conv_cols:
    top_album_songs[col] = top_album_songs[col].astype(int)
    bottom_album_songs[col] = bottom_album_songs[col].astype(int)


top_album_songs['release_date'] = pd.to_datetime(top_album_songs['release_date'])
bottom_album_songs['release_date'] = pd.to_datetime(top_album_songs['release_date'])

top_album_songs = top_album_songs.merge(genre_ohe_df, how='inner', on='reviewid')
bottom_album_songs = bottom_album_songs.merge(genre_ohe_df, how='inner', on='reviewid')



# Scrape Song Lyrics from Genius
# Enter Genius Credentials

GENIUS_CLIENT_ID = 'YOUR_GENIUS_CLIENT_ID'
GENIUS_API_SECRET = 'YOUR_GENIUS_API_SECRET'
GENIUS_API_TOKEN = 'YOUR_GENIUS_API_TOKEN'

def clean_lyrics_query(name):
    clean_name = ''.join([x if ord(x) != 160 else ' ' for x in name])    
    clean_name = clean_name.lower()
    clean_name = re.sub('ö', 'o', clean_name)
    clean_name = re.sub("[\(\[].*?[\)\]]", "", clean_name).strip()
    clean_name = re.sub(' & ', ' and ', clean_name)
    clean_name = re.sub('-', ' ', clean_name)
    clean_name = re.sub("[,.']", '', clean_name)
    clean_name = re.sub(' +', ' ', clean_name)
    clean_name = re.sub('"', '', clean_name)
    clean_name = re.sub('!', '', clean_name)
    clean_name = re.sub(':', '', clean_name)
    clean_name = re.sub('/', ' ', clean_name)
    clean_name = re.sub(r'[^0-9A-Za-z ]', '', clean_name)
    clean_name = re.sub("o clock", "oclock", clean_name)
    clean_name = clean_name.strip()
    
    if clean_name[-3:] == ' ep':
        clean_name = clean_name[:-3]
        
    if clean_name[-4:] == ' ost':
        clean_name = clean_name[:-4]
        
    return clean_name

def song_search(song_name, page):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search?per_page=50&page=' + str(page)
    data = {'q': song_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response

def request_song_url(song_name, artist_name, album_name, song_cap, page_cap):
    page = 1
    songs = []
    artist_name_query = clean_lyrics_query(artist_name)
    album_name_query = clean_lyrics_query(album_name)
    song_name_query = clean_lyrics_query(song_name)
    
    while True:
        if artist_name == 'various artists':
            search_query = song_name_query + ' ' + album_name_query
        else:
            search_query = song_name_query + ' ' + artist_name_query

        response = song_search(search_query, page)
        if 'json' in response.headers.get('Content-Type'):
            json = response.json()

            # Collect up to song_cap song objects from artist
            song_info = []
            for hit in json['response']['hits']:

                search_result_artist = clean_lyrics_query(hit['result']['primary_artist']['name'])
                search_result_song = clean_lyrics_query(hit['result']['title'])

                if (artist_name != 'various artists'):
                    if (artist_name_query in search_result_artist) and (search_result_song in song_name_query):
                        song_info.append(hit)

            # Collect song URLs from song objects
            for song in song_info:
                if (len(songs) < song_cap):
                    url = song['result']['url']
                    songs.append(url)

            if (len(songs) == song_cap) or (page == page_cap):
                break
            else:
                page += 1
        else:
            print('Response content not in JSON format.')
    
    return songs


def scrape_lyrics(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    if html.find('div', class_='lyrics') != None:
        lyrics = html.find('div', class_='lyrics').get_text()
    
        # Remove parenthetical identifiers
        lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)

        # Remove empty lines
        lyrics = os.linesep.join([s for s in lyrics.splitlines() if s])
    else:
        lyrics = 'lyrics not found'
    
    return lyrics


top_album_songs['song_lyrics'] = 'lyrics not found'
bottom_album_songs['song_lyrics'] = 'lyrics not found'


def add_lyrics(df):
    for df_index in range(len(df)):
        if df_index % 50 == 0:
            print('{}% Completed'.format(round(100*df_index/len(df), 1)))
        artist_lookup = df.iloc[df_index]['artist_name']
        song_lookup = clean_name(df.iloc[df_index]['song_name'])
        album_lookup = df.iloc[df_index]['album_title']
        songs = request_song_url(song_lookup, artist_lookup, album_lookup, 1, 1)
        
        if len(songs) == 0:
            truncated_song_lookup = song_lookup
            while len(truncated_song_lookup.split(' ')) > 1:
                truncated_song_lookup = ' '.join(truncated_song_lookup.split(' ')[:-1])
                songs = request_song_url(truncated_song_lookup, artist_lookup, album_lookup, 1, 1)
                if len(songs) > 0:
                    break
            
        if (len(songs) > 0):
            df.iloc[df_index, df.columns.get_loc('song_lyrics')] = scrape_lyrics(songs[0])
        else:
            print('lyrics not found: {} - {}'.format(df.iloc[df_index]['artist_name'], 
                                                     df.iloc[df_index]['song_name'].split('-')[0]))
        
    return df
            

top_album_songs = add_lyrics(top_album_songs)

bottom_album_songs = add_lyrics(bottom_album_songs)

top_album_songs.loc[top_album_songs['song_lyrics'] == '', 'song_lyrics'] = 'lyrics not found'
bottom_album_songs.loc[bottom_album_songs['song_lyrics'] == '', 'song_lyrics'] = 'lyrics not found'


# Save dataframes as CSV files


top_album_songs.to_csv('top_album_songs.csv', index=False)
bottom_album_songs.to_csv('bottom_album_songs.csv', index=False)

top_albums.to_csv('top_albums.csv', index=False)
bottom_albums.to_csv('bottom_albums.csv', index=False)

scores.to_csv('album_scores.csv', index=False)
genre_ohe_df.to_csv('album_genres.csv', index=False)

top_albums.iloc[missing_top_album_indices].to_csv('missing_top_albums.csv', index=False)
bottom_albums.iloc[missing_bottom_album_indices].to_csv('missing_bottom_albums.csv', index=False)