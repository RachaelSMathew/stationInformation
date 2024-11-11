import urllib.request
import json
import os
import sys ## access parameters (sys.argv is array)
from fastapi import FastAPI, Request
from haversine import haversine, Unit
## setting enviorment vars in termial: https://askubuntu.com/a/58828
## eval(String)
## os.environ['latitude'] returns a String
## if you pass an object into function, object wil get updated

## MAIN
class Tree:
    def __init__(self, val, left, right):
        self.left = left
        self.right = right
        self.val = val

app = FastAPI()
muralCoords = []
kdTree = None

@app.get("/")
def defaultFunc():
    global kdTree
    muralCoords = getCoordinates('https://data.cityofchicago.org/resource/we8h-apcf.json')
    kdTree = createKDTree(muralCoords, 'latitude')
    return kdTree

def getCoordinates(url):
    response = urllib.request.urlopen(url)
    data = json.load(response)
    ## convert all latitude and longitude in each object to float
    for object in data:
        object["latitude"] = float(object["latitude"])
        object["longitude"] = float(object["longitude"])
    return data

def createKDTree(coords, axis):
    if(len(coords) == 1): return Tree(coords[0], None, None)
    if(len(coords) == 0): return None
    
    coords.sort(key=lambda x: x[axis])
    mid = int(len(coords)/2)
    rootNode = coords[mid]
    root = Tree(rootNode, None, None)
    root.left = createKDTree(coords[:mid], 'latitude' if axis == 'longitude' else 'longitude') ## left node
    root.right = createKDTree(coords[mid+1:], 'latitude' if axis == 'longitude' else 'longitude') ## right node
    return root

@app.get("/newsearch/lat={lat}long={long}")
def newsearch(lat: float, long: float):
    global kdTree
    target = {'latitude': lat, 'longitude': long}
    closestPoints = []

    for i in range(100):
        closestObj = getNearest(kdTree, target, 'latitude')
        if(closestObj == None): break
        point = (closestObj.val['latitude'], closestObj.val['longitude'])
        addToArr = closestObj.val
        addToArr["dist"] = haversine(point, (lat, long), unit=Unit.MILES)
        closestPoints.append(addToArr)
        kdTree = deleteNode(closestObj, kdTree, 'latitude')
    
    ## check if locations repeat!
    noRepeats = []
    for i in closestPoints:
        noRepeats.append(i["mural_registration_id"])
        print(i["dist"])
    if(len(noRepeats) == len(set(noRepeats))):
        print("No repeated locations!")

    return closestPoints
    
def getNearest(root, target, axis): ## https://www.youtube.com/watch?v=Glp7THUpGow
    ## (visual of exception: https://drive.google.com/file/d/1IbuNENnNDhXTKFEe0Dm7rOzIozFRNBmp/view?usp=sharing)
    if(root == None): return None
    nextBranch = None
    otherBranch = None
    
    if(root.val[axis] < target[axis]):
        nextBranch = root.right
        otherBranch = root.left
    else:
        nextBranch = root.left
        otherBranch = root.right
    
    temp = getNearest(nextBranch, target, 'latitude' if axis == 'longitude' else 'longitude')
    best = root if (temp == None or abs(target[axis]-temp.val[axis]) > abs(target[axis]-root.val[axis])) else temp
    
    distToBest = target[axis]-best.val[axis]
    distToCurrIndex = target[axis]-root.val[axis]
    
    if(distToBest * distToBest >= distToCurrIndex * distToCurrIndex):
        temp = getNearest(otherBranch, target, 'latitude' if axis == 'longitude' else 'longitude')
        best = root if (temp == None or abs(target[axis]-temp.val[axis]) > abs(target[axis]-root.val[axis])) else temp

    return best ## return object of nearest coordinate

def findMin(root, currAxis, axis): ## return object of min in tree
    if(root == None): return None
    if(currAxis == axis):
        if(root.left == None): return root
        else:
            return findMin(root.left, 'latitude' if currAxis == 'longitude' else 'longitude', axis)
    else:
        leftMin = findMin(root.left, 'latitude' if currAxis == 'longitude' else 'longitude', axis)
        rightMin = findMin(root.right, 'latitude' if currAxis == 'longitude' else 'longitude', axis)
        mostMin = root
        if(rightMin and mostMin.val[axis] > rightMin.val[axis]): mostMin = rightMin
        if(leftMin and mostMin.val[axis] > leftMin.val[axis]): mostMin = leftMin
        return mostMin

def deleteNode(target, root, currAxis): ## https://www.cs.cmu.edu/~ckingsf/bioinfo-lectures/kdtrees.pdf
    if(root == None): return None
    nextAxis = 'latitude' if currAxis == 'longitude' else 'longitude'
    
    ## point to delete
    if(target.val["mural_registration_id"] == root.val["mural_registration_id"]):
        if(root.right):
            minObj = findMin(root.right, nextAxis, currAxis)
            root.val = minObj.val
            root.right = deleteNode(minObj, root.right, nextAxis)
        elif(root.left):
            minObj = findMin(root.left, nextAxis, currAxis)
            root.val = minObj.val
            ## swap left and right subtrees of the node that's being deleted
            root.right = deleteNode(minObj, root.left, nextAxis)
            root.left = None
        else: ## leaf node (no right or left node)
            root = None

    
    ## still need to search for point
    elif target.val[currAxis] == root.val[currAxis]: ## check both sides
        prevLeft = root.left
        root.left = deleteNode(target, root.left, nextAxis)
        if(root.left == prevLeft):
            root.right = deleteNode(target, root.right, nextAxis)

    elif target.val[currAxis] < root.val[currAxis]:
        root.left = deleteNode(target, root.left, nextAxis)

    else:
        root.right = deleteNode(target, root.right, nextAxis)

    return root


''' example structure data of each art_piece:
    "park_name": "HUMBOLDT (BARON VON)",
    "park_number": "219",
    "art": "Interpreting Nature",
    "artist": "Roman Villareal",
    "owner": "CPD",
    "x_coordinate": "1156808.64946",
    "y_coordinate": "1909066.8679200001",
    "latitude": "41.906255000000002",
    "longitude": "-87.699420000000003",
    "location": {
      "latitude": "41.906255",
      "longitude": "-87.69942"
    },
    ":@computed_region_rpca_8um6": "4",
    ":@computed_region_vrxf_vc4k": "25",
    ":@computed_region_6mkv_f3dw": "22535",
    ":@computed_region_bdys_3d7i": "301",
    ":@computed_region_43wa_7qmu": "49",
    ":@computed_region_awaf_s7ux": "10"
  },

def swapSubTrees(index, arrTree, level, lenTree): ## swap the subtrees (children of current node i.e. index)
    if(index >= lenTree or (index*2+1 >= lenTree and index*2+2 >= lenTree)): return lenTree
    startingIndex = index*2+1
    endingIndex = startingIndex + (math.pow(2, level)-1)
    if(endingIndex >= lenTree):
        for i in range(endingIndex-lenTree+1):
            arrTree.append({})
        lenTree = lenTree + (endingIndex-lenTree+1)
    ## swap subtrees
    temp = arrTree[startingIndex:startingIndex+int(math.pow(2, level)/2)]
    arrTree[startingIndex:startingIndex+int(math.pow(2, level)/2)] = arrTree[startingIndex+int(math.pow(2, level)/2):endingIndex+1]
    arrTree[startingIndex+int(math.pow(2, level)/2):endingIndex+1] = temp
    lenTree = swapSubTrees(index*2+1, arrTree, level+1, lenTree)
    lenTree = swapSubTrees(index*2+2, arrTree, level+1, lenTree)
    return lenTree
'''
