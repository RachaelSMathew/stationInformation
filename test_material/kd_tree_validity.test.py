from haversine import haversine
import json
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
## os.path.dirname(__file__) == '/Users/rachaelmathew/stationInformation/test_material'
sys.path.append(parent_dir)
import collectPointsKDTree


files = ['test_material/chicago_coordinates_latitude_variance.json', 'test_material/chicago_coordinates_longitude_variance.json', 'test_material/chicago_coordinates_within_two_miles.test.json']

for file in files:
    points = []
    with(open(file, 'r')) as f:
        points = json.load(f)

    kdTree = collectPointsKDTree.createKDTree(points, collectPointsKDTree.whichAxisSplitShouldBe(points))
    coord_in_chicago = {'latitude': 47.8832, 'longitude': -87.6424}
    coord_in_south_carolina = {'latitude': 34.0522, 'longitude': -81.0559}
    for coord in [coord_in_chicago, coord_in_south_carolina]:
        closestPoints = (collectPointsKDTree.newsearch(coord['latitude'], coord['longitude'], 0, len(points)))
        startingPoint = closestPoints[0]
        fullyConsectutive = True
        for i in range(1, len(points)):
            if(startingPoint[0] > closestPoints[i][0]):
                print('Starting point is not closer than the ${i}th closest point');
                fullyConsectutive = False
                break;
            startingPoint = closestPoints[i]
        if(fullyConsectutive):
            print('All', len(points), 'points are consecutive');