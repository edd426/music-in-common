from bottle import route, run, request
import spotipy
from spotipy import oauth2
import pprint
import json
from getUserDataUtils import getTopArtists

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '550663057de643b78fc270e67cdfaa49'
SPOTIPY_CLIENT_SECRET = '0f92dd717f5c4d3eb5713ff6b0c6462f'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-top-read' #change this for scope
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
        return getTopArtists(sp)

        '''
        for term in ['long_term', 'medium_term', 'short_term']:
            all_artists = []
            all_tracks = []
            results = sp.current_user_top_artists(limit=49, offset=0, time_range=term)
            all_artists += results['items']
            results = sp.current_user_top_artists(limit=50, offset=49, time_range=term)
            all_artists += results['items']

            results = sp.current_user_top_tracks(limit=49, offset=0, time_range=term)
            all_tracks += results['items']
            results = sp.current_user_top_tracks(limit=50, offset=49, time_range=term)
            all_tracks += results['items']


            artists = []
            for item in all_artists:
                artists.append(item['name'])
            pp.pprint(artists)

            tracks = []
            for item in all_tracks:
                tracks.append(item['name'])
            pp.pprint(tracks)
            
            #pp.pprint(results)
        
            with open('top99Artists' + USERNAME + '_' + term, 'w') as fout:
                json.dump(all_artists, fout)

            with open('top99Tracks' + USERNAME + '_' + term, 'w') as fout:
                json.dump(all_tracks, fout)

        return '<pre>' + json.dumps(all_artists+all_tracks, indent=4) + '</pre>'

        #print(len(all_artists))
        '''

        '''
        sp.trace = False
        ranges = ['short_term', 'medium_term', 'long_term']
        for myrange in ranges:
            print ("range:", myrange)
            results = sp.current_user_top_tracks(time_range=myrange, limit=50)
            for i, item in enumerate(results['items']):
                print (i, item['name'], '//', item['artists'][0]['name'])
            print()
        '''
    

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

