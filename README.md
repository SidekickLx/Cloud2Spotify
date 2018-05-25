# Cloud2Spotify
Transfer song lists from 163 Cloud music to Spotify
### Usage
```shell
$ python Cloud2Spotify.py [--daily] [--sync] -u <cloudid> -p <cloudpwd> -U <spotifyid>
```
[--daily] is to transfer your daily recommendation of 163Cloud music to Spotify.

[--sync] is to synchronize all of your playlist to Spotify.

You have to use your Spotify Username rather than your nick name which is shown at your personal dashboard(https://www.spotify.com/us/account/overview/)

Packages:
* requests
* BeautifulSoup4
* spotipy
* NetCloud

### Aboud NetCloud
[NetCloud](https://github.com/Lyrichu/NetCloud) is a Library for crawling comments and lyric from 163Cloud music.

In this project, I use netcloud to simulate user login and get user's personal informations, such as daily recommendation and playlists created or collected by users.