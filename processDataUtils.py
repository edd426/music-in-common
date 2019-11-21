import spotipy
from spotipy import oauth2
import pprint
import json
import operator

evanid = '126614655'
datadir = './data/topArtists/'
recThres = .001
# options for recommendation 
multiRankBias = False  # preference to artists in more than one ranking
normMultiGenre = True  # normalize by number of genres for the artist
rankNormalization = False  # preference to artists with higher rank

term = ['short', 'medium', 'long']

pp = pprint.PrettyPrinter(indent=2)

def processTopArtists(mydata):
    users = [evanid, mydata['id']]
    myTopArtists = {users[0]:{}, users[1]:{}}


    tmp = {}
    with open(datadir+evanid+'TopArtists.json', 'r') as f:
        tmp[users[0]] = json.load(f)
    tmp[users[1]] = mydata
    for u in users:
        for t in term:
            ranknum = 1
            for ar in tmp[u]['top_artists_'+t+'_term']:
                if ar['id'] not in myTopArtists[u]:
                    myTopArtists[u][ar['id']] = ar
                myTopArtists[u][ar['id']]['artist'+t] = ranknum
                ranknum+=1

    # store user display names and ids
    mydata['users'] = {users[0]:{}, users[1]:{}}
    mydata['users'][users[0]]['display_name'] = tmp[users[0]]['display_name']
    mydata['users'][users[1]]['display_name'] = tmp[users[1]]['display_name']
    mydata['users'][users[0]]['id'] = tmp[users[0]]['id']
    mydata['users'][users[1]]['id'] = tmp[users[1]]['id']

    mydata['pTopArtists'] = myTopArtists
    return mydata

def processTopGenres(mydata):
    users = [evanid, mydata['id']]
    tmp = mydata['pTopArtists']

    user1Genre = {}
    user1NumArtists = float(len(tmp[users[0]]))
    for ar in tmp[users[0]]:
        for g in tmp[users[0]][ar]['genres']:
            if g not in user1Genre:
                user1Genre[g] = 0
            user1Genre[g] +=1


    user2Genre = {}
    user2NumArtists = float(len(tmp[users[1]]))
    for ar in tmp[users[1]]:
        for g in tmp[users[1]][ar]['genres']:
            if g not in user2Genre:
                user2Genre[g] = 0
            user2Genre[g] +=1


    for g in user1Genre:
        user1Genre[g] /= user1NumArtists
    for g in user2Genre:
        user2Genre[g] /= user2NumArtists
        
    mydata['pTopGenres'] = {}
    mydata['pTopGenres'][users[0]] = user1Genre
    mydata['pTopGenres'][users[1]] = user2Genre
    

    return mydata


def printSharedTopArtists(mydata):
    users = [evanid, mydata['id']]
    tmp = mydata['pTopArtists']
    retstr = '<pre>\n'
    retstr += "{:<30s}{:^20s}{:<10s}{:^20s}\n".format(" ", 
            mydata['users'][users[0]]['display_name'],
            " ",
            mydata['users'][users[1]]['display_name'])
    retstr += "{:<30s}{:^7s}{:^7s}{:^6s}{:^10s}{:^7s}{:^7s}{:^6s}\n".format(
            "***Shared Top Artists***",
            "short", 
            "medium",
            "long",
            " ",
            "short", 
            "medium",
            "long")
    print("Shared Top Artists")
    tdict = {'short':'*', 'medium':'*', 'long':'*'}
    for ar in tmp[users[0]]:
        if ar in tmp[users[1]]:
            match1 = tdict.copy()
            match2 = tdict.copy()
            for t in term:
                if 'artist'+t in tmp[users[0]][ar]:
                    match1[t] = tmp[users[0]][ar]['artist'+t]
                if 'artist'+t in tmp[users[1]][ar]:
                    match2[t] = tmp[users[1]][ar]['artist'+t]
                
            tmpstr = (""
                    + "{:<30s}{:^6s}|{:^6s}|{:^6s}{:^10s}{:^6s}|{:^6s}|{:^6s}".format(
                        tmp[users[0]][ar]['name'],
                        str(match1['short']),
                        str(match1['medium']),
                        str(match1['long']),
                        " ",
                        str(match2['short']),
                        str(match2['medium']),
                        str(match2['long']))
                    )
            print(tmpstr)
            retstr += tmpstr+'\n'
    retstr += '</pre>'
    return retstr


def printSharedTopGenre(mydata):
    users = [evanid, mydata['id']]
    tmp = mydata['pTopGenres']
    retstr = '<pre>\n'
    retstr += "{:<30s}{:^20s}{:^10s}{:^20s}\n".format(
            "---Shared Top Genres---",
            mydata['users'][users[0]]['display_name'], 
            "",
            mydata['users'][users[1]]['display_name'])
    print("Shared Top Genres")
    matches = {}
    for g in tmp[users[0]]:
        if g in tmp[users[1]]:
            # need to experiment with this, the metric it's sorted by
            #matches[g] = tmp[users[0]][g] + tmp[users[1]][g] - (tmp[users[0]][g]- tmp[users[1]][g])**2
            matches[g] = min(tmp[users[0]][g], tmp[users[1]][g])
    for g in sorted(matches.items(), key=lambda kv: kv[1], reverse=True):
        if g[1] < 0.02:
            break
        tmpstr = (""
                + "{:<30s}{:^20.2%}{:^10s}{:^20.2%}".format(
                    g[0],
                    tmp[users[0]][g[0]],
                    "",
                    tmp[users[1]][g[0]])
                )
        print(tmpstr)
        retstr += tmpstr+'\n'
    retstr += '</pre>'
    return retstr

def printRecommendedArtists(mydata):
    termset = {'artistshort', 'artistmedium', 'artistlong'}
    users = [evanid, mydata['id']]
    tmpA = mydata['pTopArtists']
    tmpG = mydata['pTopGenres']
    print("\n$$$Recommended Artists From Evan$$$")
    retstr = '<pre>\n'
    retstr += "{:<40s}{:^20s}\n".format('$$$Recommended Artists From Evan$$$', 'score')

    user1RecArtists = {}
    for a in tmpA[users[0]]:
        if a not in tmpA[users[1]]:
            user1RecArtists[a] = 0
            for g in tmpA[users[0]][a]['genres']:
                if g in tmpG[users[1]]:
                    # bias for artists who are in multiple top time periods (seems to be bias toward long-term)
                    numranks = 1 # default no biasing
                    normGenres = 1 # defualt no normalization
                    rankNorm = 1
                    if multiRankBias:
                        numranks = len(termset.intersection(set(tmpA[users[0]][a].keys())))
                    if normMultiGenre:
                        normGenres = (1./len(tmpA[users[0]][a]['genres']))
                    if rankNormalization:
                        for t in term:
                            if 'artist'+t in tmpA[users[0]][a]:
                                rankNorm += tmpA[users[0]][a]['artist'+t]
                        rankNorm /= len(termset.intersection(set(tmpA[users[0]][a].keys())))
                        rankNorm =  ((100-rankNorm)/(2*100)) + .5
                    user1RecArtists[a] += tmpG[users[1]][g] * numranks * normGenres * rankNorm 

    for a in sorted(user1RecArtists.items(), key=lambda kv: kv[1], reverse=True):
        if user1RecArtists[a[0]] <= recThres:
            break
        tmpstr = "{:<40s}{:^20.3f}".format(
                 tmpA[users[0]][a[0]]['name'], 
                 user1RecArtists[a[0]])
        print(tmpstr)
        retstr += tmpstr+'\n'
    retstr += '</pre>'


    print("\n@@@Artists to Recommend to Evan@@@")
    retstr += '<pre>\n'
    retstr += "{:<40s}{:^20s}\n".format('@@@Artists to Recommend to Evan@@@', 'score')
    user2RecArtists = {}
    for a in tmpA[users[1]]:
        if a not in tmpA[users[0]]:
            user2RecArtists[a] = 0
            for g in tmpA[users[1]][a]['genres']:
                if g in tmpG[users[0]]:
                    # bias for artists who are in multiple top time periods
                    numranks = 1
                    normGenres = 1
                    rankNorm = 1
                    if multiRankBias:
                        numranks = len(termset.intersection(set(tmpA[users[1]][a].keys())))
                    if normMultiGenre:
                        normGenres = (1./len(tmpA[users[1]][a]['genres']))
                    if rankNormalization:
                        for t in term:
                            if 'artist'+t in tmpA[users[1]][a]:
                                rankNorm += tmpA[users[1]][a]['artist'+t]
                        rankNorm /= len(termset.intersection(set(tmpA[users[1]][a].keys())))
                        rankNorm =  ((100-rankNorm)/(2*100)) + .5
                    user2RecArtists[a] += tmpG[users[0]][g] * numranks * normGenres * rankNorm

    for a in sorted(user2RecArtists.items(), key=lambda kv: kv[1], reverse=True):
        if user2RecArtists[a[0]] < recThres:
            break
        tmpstr = "{:<40s}{:^20.3f}".format(
                tmpA[users[1]][a[0]]['name'], 
                user2RecArtists[a[0]])
        print(tmpstr)
        retstr += tmpstr+'\n'

    retstr += '</pre>'
    return retstr

def loadUserData(userid):
    with open(datadir+'/'+userid+'topArtists', 'r') as f:
        tmp = json.load(f)
    return tmp



#def main():
#    mydata = {}
#    mydata = getTopArtists(user1, user2, mydata)
#    mydata = getGenreFromArtists(mydata)
#    #printSharedTopArtists(mydata)
#    printSharedTopGenre(mydata)
#    recommendArtists(mydata)


if __name__ == '__main__':
    main()

