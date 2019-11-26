import spotipy
from spotipy import oauth2
import pprint
import json

pp = pprint.PrettyPrinter(indent=3)
LIB_LIMIT = 10000

# sp requires user-top-read
# if retDict is passed in
def getTopArtists(sp, retDict = None, store=True):

    myDict = {}

    # TODO take out this api call
    userdata = getUser(sp)
    myDict['id'] = userdata['id']
    myDict['display_name'] = userdata['display_name']
    

    for term in ['short_term', 'medium_term', 'long_term']:
        all_artists = []
        results = sp.current_user_top_artists(limit=49, offset=0, time_range=term)
        all_artists += results['items']
        results = sp.current_user_top_artists(limit=50, offset=49, time_range=term)
        all_artists += results['items']
        myDict['top_artists_'+term] = all_artists

    myDict['num_top_artists'] = len(all_artists)

    if store:
        outfile = './data/topArtists/' + myDict['id']+'TopArtists.json'
        with open(outfile, 'w') as fout:
            json.dump(myDict, fout)
    if retDict is None:
        retDict = myDict
    else:
        retDict.update(myDict)

    return retDict


def printUserTopArtists(mydata):
    
    sortedArtists ={'short_term':99*[""], 'medium_term':99*[""], 'long_term':99*[""]}
    print("%%%Top Artists of " + mydata['display_name']+"%%%")
    retStr = "<pre>\n"
    retStr += "{:<30s}\n".format("%%%Top Artists of " + mydata['display_name']+"%%%")
    retStr += "{:<6}{:<30s}{:<30s}{:<30s}\n".format(
            "Rank",
            "Short Term (4 Weeks)", 
            "Medium Term (6 Months)",
            "Long Term (All Time)")

    for term in ['short_term', 'medium_term', 'long_term']:
        all_artists = mydata['top_artists_'+term]
        counter = 0
        for a in all_artists:
            sortedArtists[term][counter]=a['name']
            counter+=1
    counter = 0
    for a in range(99):
        tmpStr = "{:<6s}{:<30s}{:<30s}{:<30s}\n".format(
                str(counter + 1),
                sortedArtists['short_term'][counter],
                sortedArtists['medium_term'][counter],
                sortedArtists['long_term'][counter]
            )
        counter += 1
        print(tmpStr)
        retStr+=tmpStr
    retStr +='</pre>'

    return retStr


def loadTopArtists(loadid):

    datadir = '/home/eddelord/Documents/spotify/data/topArtists/'
    with open(datadir+loadid+'TopArtists.json', 'r') as f:
        tmp = json.load(f)
    return tmp


def getTopTracks(sp, retDict=None, store=True):
    
    myDict = {}
    userdata = getUser(sp)
    myDict['id'] = userdata['id']
    myDict['display_name'] = userdata['display_name']

    for term in ['long_term', 'medium_term', 'short_term']:
        all_tracks = []
        results = sp.current_user_top_tracks(limit=49, offset=0, time_range=term)
        all_tracks += results['items']
        results = sp.current_user_top_tracks(limit=50, offset=49, time_range=term)
        all_tracks += results['items']
        myDict['top_tracks_'+term] = all_tracks

    myDict['num_top_tracks'] = len(all_tracks)
    myDict['top_tracks'] = all_tracks

    if store:
        outfile = './data/topTracks/' + myDict['id']+'TopTracks.json'
        with open(outfile, 'w') as fout:
            json.dump(myDict, fout)

    if retDict is None:
        retDict = myDict
    else:
        retDict.update(myDict)

    return retDict

def getLibraryTracks(sp, retDict=None, store=True):

    all_tracks = []
    for i in range(0, LIB_LIMIT, 50):
        results = sp.current_user_saved_tracks(limit=50, offset=i)
        if results is None:
            break
        all_tracks += results['items']

    myDict = {}
    userdata = getUser(sp)
    myDict['id'] = userdata['id']
    myDict['display_name'] = userdata['display_name']
    myDict['num_lib_tracks'] = len(all_tracks)
    myDict['lib_tracks'] = all_tracks

    if store:
        outfile = './data/library/' + myDict['id']+'LibTracks.json'
        with open(outfile, 'w') as fout:
            json.dump(myDict, fout)

    if retDict is None:
        retDict = myDict
    else:
        retDict.update(myDict)

    return retDict

def getFollowArtists(sp, retDict=None, store=True):

    all_artists = []
    results = sp.current_user_followed_artists(limit=50)
    all_artists += results['artists']['items']
    while(results['artists']['next'] is not None):
        results = sp.current_user_followed_artists(limit=50, after=results['artists']['cursors']['after'])
        all_artists += results['artists']['items']

    myDict = {}
    userdata = getUser(sp)
    myDict['id'] = userdata['id']
    myDict['display_name'] = userdata['display_name']
    myDict['num_fol_artists'] = len(all_artists)
    myDict['fol_artists'] = all_artists

    if store:
        outfile = './data/followed/' + myDict['id']+'FolArtists.json'
        with open(outfile, 'w') as fout:
            json.dump(myDict, fout)

    if retDict is None:
        retDict = myDict
    else:
        retDict.update(myDict)

    return retDict


def getUser(sp, retDict=None):
    userdata = sp.current_user()
    if retDict is None:
        return userdata
    retDict['id'] = userdata['id']
    retDict['display_name'] = userdata['display_name']
    return retDict

