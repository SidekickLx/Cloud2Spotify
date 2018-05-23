# -*- coding: utf-8 -*-
import sys
import re
import requests
from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util
import json

headers = {
    'Referer' : "http://music.163.com/",
    'Host' : 'music.163.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Ic',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

def get_list(id) :
    songlist = []
    play_url = 'http://music.163.com/playlist?id='+str(id)
    s = requests.session()
    s = BeautifulSoup(s.get(play_url, headers = headers).content, 'lxml')
    main = s.find('ul', {'class' : 'f-hide'})
    title = s.find('h2').get_text()
    for music in main.find_all('a') :
        singer_url = 'http://music.163.com'+music['href']
        s2 = requests.session()
        s2 = BeautifulSoup(s2.get(singer_url,headers = headers).content,'lxml')
        des=s2.find('script',type="application/ld+json").get_text()
        desb = json.loads(des)
        singer = desb['description'].split('。')[0].split('：')[1]
        song = [desb['title'], singer]
        songlist.append(song)
    return songlist, title
    
def spotify_auth(username) :
    token = util.prompt_for_user_token(
                                        username,
                                        'playlist-modify-private playlist-modify-public',
                                        client_id='d8e14152c17e4be7bbc94567e5aad4ac',
                                        client_secret='7a71734548944c9d802d321cd30b5014',
                                        redirect_uri='https://github.com/SidekickLx/Cloud2Spotify/'
                                        )
    if token :
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
    return sp

def get_list_id_by_name(sp, username, list_name) :
    playlists = sp.user_playlists(username)
    for playlist in playlists['items']:
        if list_name == playlist['name']:
            list_id = playlist['id']
            return list_id
    return ''
    
def set_spotify_playlist(sp, username, list_name) : 
    list_id = get_list_id_by_name(sp, username, list_name)
    if list_id == '' :
        sp.user_playlist_create(username, list_name)
        list_id = get_list_id_by_name(sp, username, list_name)  
    return list_id  


if __name__ == "__main__" :
    cloud_list_id = "162499819"
    username = "9sbqcfyysw4ew7ltg9svtla1v"
    description = 'Playlist from Cloud music'
    sp = spotify_auth(username)  
    cloud_songlist, list_name = get_list(cloud_list_id)
    print("Creating a new list: ", list_name)
    spotify_list_id = set_spotify_playlist(sp, username, list_name)
    count = 0
    for song, singer in cloud_songlist :
        r_chinese_bracket = re.compile(r'\（.*?\）' )
        r_english_bracket = re.compile(r'\(.*?\)' )
        main_title = r_chinese_bracket.sub('', song)
        main_title = r_english_bracket.sub('', main_title)
        results = sp.search(q='track:' + main_title, type='track')
        items = results["tracks"]["items"]
        spotify_uri_list = []
        for item in items :
            artist_results = sp.search(q='artist:' + singer, type='artist')
            artist_items = artist_results['artists']['items']
            if len(artist_items) > 0:
                artist = artist_items[0]
                if str(item['artists'][0]['name']) == artist['name'] :
                    print(item['name'] + ' - ' + item['artists'][0]['name'])
                    spotify_uri_list.append(item['uri'])
                    sp.user_playlist_add_tracks(username, spotify_list_id, spotify_uri_list)
                    spotify_uri_list.clear()
                    count = count + 1
                    break    
    print("Songs from Cloud music: ", len(cloud_songlist), "Songs added to Spotify: ", count)
    
