import urllib.request
import json
from haversine import haversine, Unit
import os
from dotenv import load_dotenv, find_dotenv, set_key
import sys ## access paramters (sys.argv is array)
## setting enviorment vars in termial: https://askubuntu.com/a/58828
## eval(String)
## os.environ['latitude'] returns a String

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)  # This line brings all environment variables from .env into os.environ

def getCoordinates(url):
    response = urllib.request.urlopen(url)
    data = json.load(response)
    return data['data']['stations']


def getHaversine(array): ## Calculate the distance in mi. between two cooridnates (haversine formula)
    distDict = {} ## {rounded int distance between each coord and reference coordinate: {exact float distance of coord to reference: {station info}}}
    for coord in array:
        currPoint = (coord['lat'], coord['lon'])
        dist = haversine(currPoint, refPoint, unit='mi')
        if int(dist) in distDict:
            distDict[int(dist)][dist] = coord
        else:
            distDict[int(dist)] = {dist: coord}

    for distance in distDict:
        distanceInfoArr = distDict[distance]
        sortedDistances = list(distanceInfoArr.keys()) ## keys() returns array
        sortedDistances.sort() ## sort() has no return type
        distDict[distance] = {i: distanceInfoArr[i] for i in sortedDistances}
    return distDict

def getMore(dist, lat, lon, arr):
    moreArr = {}
    if int(dist) in arr:
        for station in arr[int(dist)].values():
            haverDist = haversine((lat, lon), (station['lat'], station['lon']), unit='mi')
            moreArr[haverDist] = station
    return moreArr

def getClosest(lat, lon, arr, lDeviation, rDeviation, results):
    dist = haversine((lat, lon), refPoint, unit='mi')

    if results == {} and lDeviation == 1 and rDeviation == 1: ## new coordinate search
        results.update(getMore(int(dist), lat, lon, arr))

    leftDistances = getMore(int(dist)-lDeviation, lat, lon, arr)
    results.update(leftDistances)
    while len(leftDistances) == 0 and list(arr.keys())[0] <= int(dist)-(lDeviation+1):
        lDeviation = lDeviation + 1;
        leftDistances = getMore(int(dist)-lDeviation, lat, lon, arr)
        results.update(leftDistances)

    rightDistances = getMore(int(dist)+rDeviation, lat, lon, arr)
    results.update(rightDistances)
    while len(rightDistances) == 0 and list(arr.keys())[-1] >= int(dist)+(rDeviation+1):
        rDeviation = rDeviation + 1
        rightDistances = getMore(int(dist)+rDeviation, lat, lon, arr)
        results.update(rightDistances)

    distancesSorted = list(results.keys())
    distancesSorted.sort()
    results = {i: results[i] for i in distancesSorted}

    for result in list(results.keys())[:10]: ## print first 10 results
        print(str(result)+'\t'+results[result]['name']+'\n')

    # Write changes to .env file.
    set_key(dotenv_file, "results", str({i: results[i] for i in list(results.keys())[10:]}))
    if len(sys.argv) > 2:
        set_key(dotenv_file, "latitude", sys.argv[1])
        set_key(dotenv_file, "longitude", sys.argv[2])
    set_key(dotenv_file, "rDeviation", str(rDeviation))
    set_key(dotenv_file, "lDeviation", str(lDeviation))


## MAIN ##
lDeviation = eval(os.environ['lDeviation'])
rDeviation = eval(os.environ['rDeviation'])
results = eval(os.environ['results']) ## results needs to be initialized to {} i env file. String dict to dict (json.loads requires results variable to be stored in double quotes, eval is more flexible)

if results == {} and sys.argv[1] == 'loadmore':
    print("you need to input coordinates first!")

elif results != {} and len(results.keys()) >= 10 and sys.argv[1] == 'loadmore': ## load more
    for result in list(results.keys())[:10]:
        print(str(result)+'\t'+results[result]['name']+'\t'+("has kiosk" if results[result]['has_kiosk'] else "no kiosk")+'\n')
    # Write changes to .env file.
    set_key(dotenv_file, "results", str({i: results[i] for i in list(results.keys())[10:]}))

else:
    stations = getCoordinates('https://gbfs.citibikenyc.com/gbfs/en/station_information.json')
    refLat = stations[0]['lat']
    refLon = stations[0]['lon']
    refPoint = (refLat, refLon)
    if sys.argv[1] == 'loadmore':
        getClosest(float(os.environ['latitude']), float(os.environ['longitude']), getHaversine(stations), lDeviation, rDeviation, results)
    else: ## new search with new current coord. (whenever no param of 'loadmore')
        results = {}
        lDeviation = 1
        rDeviation = 1
        getClosest(float(sys.argv[1]), float(sys.argv[2]), getHaversine(stations), lDeviation, rDeviation, results)


## data of each station: {'station_type': 'classic', 'has_kiosk': True, 'name': 'Madison St & Seneca Ave', 'external_id': '26cae473-0e59-4af7-bad5-bb6fec85c8bc', 'electric_bike_surcharge_waiver': False, 'lat': 40.70183, 'rental_methods': ['KEY', 'CREDITCARD'], 'station_id': '26cae473-0e59-4af7-bad5-bb6fec85c8bc', 'rental_uris': {'android': 'https://bkn.lft.to/lastmile_qr_scan', 'ios': 'https://bkn.lft.to/lastmile_qr_scan'}, 'capacity': 3, 'eightd_station_services': [], 'lon': -73.90625, 'short_name': '4880.11', 'eightd_has_key_dispenser': False, 'region_id': '71'}

## https://stackoverflow.com/a/60354400 (we can't update the enviormental variables in terminal with a child shell process)

## env file components: latitude, longitude(current search coordinates), results(search results for current coordinates), lDeviation, rDeviation
