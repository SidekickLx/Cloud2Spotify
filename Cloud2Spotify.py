# -*- coding: utf-8 -*-
import sys
import getopt
import re
import time
import requests
from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util
import json
from NetCloud.NetCloudLogin import NetCloudLogin

headers = {
    'Referer' : "http://music.163.com/",
    'Host' : 'music.163.com',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Ic',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}


def cloud_music_get_daily_recommend(username, pwd) : 
    daily_recommend = []
    list_name = time.strftime("%m/%d/%y") + " Daily Recommend"
    phone = username
    password = pwd
    email = None
    rememberLogin = True
    login = NetCloudLogin(phone = phone,password = password,email = email,rememberLogin = rememberLogin)
    recomend_song_list = login.get_self_daily_recommend().json()['recommend']
    for rcmd_song in recomend_song_list : 
        item = [rcmd_song['name'], rcmd_song['artists'][0]['name']]
        daily_recommend.append(item)
    return daily_recommend, list_name

def cloud_music_sync_playlists(username, pwd): 
    play_lists = []
    phone = username
    password = pwd
    email = None
    rememberLogin = True
    login = NetCloudLogin(phone = phone,password = password,email = email,rememberLogin = rememberLogin)
    self_playlists = login.get_self_play_list().json()['playlist']
    for playlist in self_playlists :
        play_lists.append(get_list(playlist['id']))
    return play_lists



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

def transfer_playlist(sp, spotify_username, cloud_playlist, list_name) : 
    print("Creating a new list: ", list_name)
    spotify_list_id = set_spotify_playlist(sp, spotify_username, list_name)
    count = 0
    for song, singer in cloud_playlist :
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
                    sp.user_playlist_add_tracks(spotify_username, spotify_list_id, spotify_uri_list)
                    spotify_uri_list.clear()
                    count = count + 1
                    break    
    print("Songs from Cloud music: ", len(cloud_playlist), "Songs added to Spotify: ", count)

def main(argv=None) :
    daily = False
    sync = False
    try:
        opts, args = getopt.getopt(argv, "DSu:p:U:",["daily", "sync", "cloudid=", "cloudpwd=", "spotifyid="])
    except getopt.GetoptError:
        print("Error: Cloud2Spotify.py [--daily] [--sync] -u <cloudid> -p <cloudpwd> -U <spotifyid>")
        return 2
    for opt, arg in opts:
        if opt in ("-D", "--daily"):
            daily = True
        if opt in ("-S", "--sync"):
            sync = True
        if opt in ("-u", "--cloudid"):
            cloud_username = arg
        if opt in ("-p", "--cloudpwd"):
            cloud_pwd = arg
        if opt in ("-U", "--spotifyid"):
            spotify_username = arg

    if daily : 
        cloud_playlist, list_name = cloud_music_get_daily_recommend(cloud_username, cloud_pwd)
        sp = spotify_auth(spotify_username)
        transfer_playlist(sp, spotify_username, cloud_playlist, list_name)
    if sync :
        play_lists = cloud_music_sync_playlists(cloud_username, cloud_pwd)
        sp = spotify_auth(spotify_username)
        for list_name, cloud_playlist in play_lists :
            transfer_playlist(sp, spotify_username, cloud_playlist, list_name)

    
def test() :
    title = 'title'
    songs = ['song1', 'song2']
    return title, songs

if __name__ == "__main__" :
    sys.exit(main(sys.argv[1:]))
    
