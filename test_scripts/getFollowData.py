from bottle import route, run, request
import spotipy
from spotipy import oauth2
import pprint
import json

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '550663057de643b78fc270e67cdfaa49'
SPOTIPY_CLIENT_SECRET = '0f92dd717f5c4d3eb5713ff6b0c6462f'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-follow-read' #change this for scope
CACHE = '.spotipyoauthcache'
USERNAME = 'Evan'

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

pp = pprint.PrettyPrinter(indent=4)

@route('/')
def index():

    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print ("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print ("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(auth=access_token)
        all_artists = []
        results = sp.current_user_followed_artists(limit=50)
        pp.pprint(results)
        all_artists += results['artists']['items']
        while(results['artists']['next'] is not None):
            results = sp.current_user_followed_artists(limit=50, after=results['artists']['cursors']['after'])
            all_artists += results['artists']['items']
            pp.pprint(results)
            print("another round of followed")

        artists = []
        for item in all_artists:
            artists.append(item['name'])
        pp.pprint(artists)
        numArtists = len(all_artists)
        print(numArtists)
    
        with open('followedArtists' + USERNAME+str(numArtists), 'w') as fout:
            json.dump(all_artists, fout)


        return '<pre>' + json.dumps(all_artists, indent=4) + '</pre>'

    

    else:
        return htmlForLoginButton()

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

run(host='', port=8080)

