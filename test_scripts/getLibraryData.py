from bottle import route, run, request
import spotipy
from spotipy import oauth2
import pprint
import json

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '550663057de643b78fc270e67cdfaa49'
SPOTIPY_CLIENT_SECRET = '0f92dd717f5c4d3eb5713ff6b0c6462f'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read' #change this for scope
CACHE = '.spotipyoauthcache'
USERNAME = 'Grant'
NUM_SAVED_TRACKS = 9000

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

        #all_artists = []
        #all_artists += results['items']
        all_tracks = []
        for i in range(0, NUM_SAVED_TRACKS, 50):
            results = sp.current_user_saved_tracks(limit=50, offset=i)
            if results is None:
                break
            all_tracks += results['items']
            #for item in results['items']:
            #    all_tracks += item['track']
        #pp.pprint(all_tracks)

            #artists = []
            #for item in all_artists:
            #    artists.append(item['name'])
            #pp.pprint(artists)
        
            #with open('librarySongs' + USERNAME, 'w') as fout:
            #    json.dump(all_artists, fout)
        num_tracks = len(all_tracks)
        print(num_tracks)
        with open('librarySongs' + USERNAME+'_'+str(num_tracks), 'w') as fout:
            json.dump(all_tracks, fout)

        return "<pre>" + json.dumps(results, indent=4) + "</pre>"

        #print(len(all_artists))

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


