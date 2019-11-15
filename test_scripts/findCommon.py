import spotipy
from spotipy import oauth2
import pprint
import json
import operator

user1 = 'Evan'
user2 = 'Grant'

term = ['short', 'medium', 'long']

pp = pprint.PrettyPrinter(indent=2)

def getTopArtists(user1, user2, mydata):

    datadir = '/home/eddelord/Documents/spotify/data/topArtists'

    users = [user1, user2]

    for u in users:
        if u not in mydata:
            mydata[u] = {}
        for t in term:
            with open(datadir+'/top99Artists'+u+'_'+t+'_term', 'r') as f:
                tmp = json.load(f)
                ranknum = 1
                for ar in tmp:
                    if ar['id'] not in mydata[u]:
                        mydata[u][ar['id']] = ar
                    mydata[u][ar['id']]['artist'+t] = ranknum
                    ranknum+=1

    return mydata

def getGenreFromArtists(mydata):
    user1Genre = {}
    user1NumArtists = float(len(mydata[user1]))
    for ar in mydata[user1]:
        for g in mydata[user1][ar]['genres']:
            if g not in user1Genre:
                user1Genre[g] = 0
            user1Genre[g] +=1


    user2Genre = {}
    user2NumArtists = float(len(mydata[user2]))
    for ar in mydata[user2]:
        print(mydata[user2][ar]['genres'])
        for g in mydata[user2][ar]['genres']:
            if g not in user2Genre:
                user2Genre[g] = 0
            user2Genre[g] +=1


    for g in user1Genre:
        user1Genre[g] /= user1NumArtists
    for g in user2Genre:
        user2Genre[g] /= user2NumArtists
        
    #pp.pprint(sorted(user1Genre.items(), key=lambda kv: kv[1], reverse=True))
    #pp.pprint(sorted(user2Genre.items(), key=lambda kv: kv[1], reverse=True))

    mydata[user1]['genre'] = user1Genre
    mydata[user2]['genre'] = user2Genre
    

    return mydata


def printSharedTopArtists(mydata):
    print("Shared Top Artists")
    for ar in mydata[user1]:
        if ar in mydata[user2]:
            match1 = {}#tdict.copy()
            match2 = {}#tdict.copy()
            for t in term:
                if 'artist'+t in mydata[user1][ar]:
                    match1[t] = mydata[user1][ar]['artist'+t]
                if 'artist'+t in mydata[user2][ar]:
                    match2[t] = mydata[user2][ar]['artist'+t]
            print(mydata[user1][ar]['name'] + "\n\t"+user1+"\t" 
                    +str(match1)
                    + "\n\t"+user2+"\t" 
                    +str(match2))


def printSharedTopGenre(mydata):
    print("Shared Top Genres")
    matches = {}
    for g in mydata[user1]['genre']:
        if g in mydata[user2]['genre']:
            matches[g] = mydata[user1]['genre'][g]**2 + mydata[user2]['genre'][g]**2 # sum for now, may try sum of squares later
    for g in sorted(matches.items(), key=lambda kv: kv[1], reverse=True):

        print(g[0] + "\n\t"+user1+"\t" 
                +str(mydata[user1]['genre'][g[0]])
                + "\n\t"+user2+"\t" 
                +str(mydata[user2]['genre'][g[0]])
                )

def recommendArtists(mydata):
    user1RecArtists = {}
    for a in mydata[user1]:
        if a not in mydata[user2]:
            user1RecArtists[a] = 0
            for g in mydata[user1][a]['genres']:
                if g in mydata[user2]['genre']:
                    user1RecArtists[a] += mydata[user2]['genre'][g]

    for a in sorted(user1RecArtists.items(), key=lambda kv: kv[1], reverse=True):
        print(mydata[user1][a[0]]['name'] + "\t\t" + str(user1RecArtists[a[0]]))


    user2RecArtists = {}
    for a in mydata[user2]:
        if a not in mydata[user1]:
            user2RecArtists[a] = 0
            for g in mydata[user2][a]['genres']:
                if g in mydata[user1]['genre']:
                    user2RecArtists[a] += mydata[user1]['genre'][g]

    for a in sorted(user2RecArtists.items(), key=lambda kv: kv[1], reverse=True):
        print(mydata[user2][a[0]]['name'] + "\t\t" + str(user2RecArtists[a[0]]))




def main():
    mydata = {}
    mydata = getTopArtists(user1, user2, mydata)
    mydata = getGenreFromArtists(mydata)
    #printSharedTopArtists(mydata)
    printSharedTopGenre(mydata)
    recommendArtists(mydata)


if __name__ == '__main__':
    main()

