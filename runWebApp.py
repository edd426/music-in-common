from bottle import route, run, request
import spotipy
from spotipy import oauth2
import pprint
import json
from getDataUtils import *
from processDataUtils import *
import os
print()

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID']
SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET']
SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI']
SCOPE = 'user-top-read user-library-read user-follow-read' #change this for scope
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

pp = pprint.PrettyPrinter(indent=2)

@route('/')
def index():

    access_token = ""

    #token_info = sp_oauth.get_cached_token()
    token_info = False

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
        dat = getTopArtists(sp)
        #dat = loadTopArtists('21pbazi5mi3fymvmqcir7ntei') #allen.delord2017 #116981000 #116981000 #21pbazi5mi3fymvmqcir7ntei
        dat = getTopTracks(sp, retDict=dat)
        #dat = getLibraryTracks(sp, retDict=dat)
        dat = getFollowArtists(sp, retDict=dat)
        dat = processTopArtists(dat)
        dat = processTopGenres(dat) # process Top Artists must come before. Bad Design
        outstr = printSharedTopArtists(dat)
        outstr +=printSharedTopGenre(dat)
        outstr +=printRecommendedArtists(dat)

        return outstr
    #"<pre>"+json.dumps(dat['pTopArtists'], indent=2) + "</pre>"

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

