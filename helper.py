
''' 
Example of muralCoords to test:
muralCoords =  [
    {'mural_registration_id': '19117', 'latitude': 41.90732594, 'longitude': -87.69772841, 'location': {'type': 'Point', 'coordinates': [41.90732594, -87.69772841]}},
    {'mural_registration_id': '19118', 'latitude': 41.90901393, 'longitude': -87.70716786, 'location': {'type': 'Point', 'coordinates': [41.90901393, -87.70716786]}},
    {'mural_registration_id': '19119', 'latitude': 41.88789426, 'longitude': -87.68967508, 'location': {'type': 'Point', 'coordinates': [41.88789426, -87.68967508]}},
    {'mural_registration_id': '19120', 'latitude': 41.90065775, 'longitude': -87.6918669, 'location': {'type': 'Point', 'coordinates': [41.90065775, -87.6918669]}},
    {'mural_registration_id': '19121', 'latitude': 41.91635683, 'longitude': -87.69413919, 'location': {'type': 'Point', 'coordinates': [41.91635683, -87.69413919]}},
    {'mural_registration_id': '19122', 'latitude': 41.8826137, 'longitude': -87.71134545, 'location': {'type': 'Point', 'coordinates': [41.8826137, -87.71134545]}},
    {'mural_registration_id':'19123', 'latitude': 41.90613829, 'longitude': -87.70045414, 'location': {'type': 'Point', 'coordinates': [41.90613829, -87.70045414]}},
    {'mural_registration_id':'19124', 'latitude': 41.90836466, 'longitude': -87.71019035, 'location': {'type': 'Point', 'coordinates': [41.90836466, -87.71019035]}},
    {'mural_registration_id':'19125', 'latitude': 41.90650992, 'longitude': -87.70094902, 'location': {'type': 'Point', 'coordinates': [41.90650992, -87.70094902]}},
    {'mural_registration_id':'19126', 'latitude': 41.90114777, 'longitude': -87.68872492, 'location': {'type': 'Point', 'coordinates': [41.90114777, -87.68872492]}},
    {'mural_registration_id':'19127', 'latitude': 41.90340177, 'longitude': -87.69934941, 'location': {'type': 'Point', 'coordinates': [41.90340177, -87.69934941]}},
    {'mural_registration_id':'19128', 'latitude': 41.90611369, 'longitude': -87.69639518, 'location': {'type': 'Point', 'coordinates': [41.90611369, -87.69639518]}},
    {'mural_registration_id':'19129', 'latitude': 41.91337241, 'longitude': -87.71163748, 'location': {'type': 'Point', 'coordinates': [41.91337241, -87.71163748]}},
    {'mural_registration_id':'19130', 'latitude': 41.88978511, 'longitude': -87.71139384, 'location': {'type': 'Point', 'coordinates': [41.88978511, -87.71139384]}},
    {'mural_registration_id':'19131', 'latitude': 41.89584217, 'longitude': -87.69255831, 'location': {'type': 'Point', 'coordinates': [41.89584217, -87.69255831]}}
]
'''

def findMin(root, currAxis, axis): ## return object of min in tree
    if(root == None): return None
    if(currAxis == axis):
        if(root.left == None): return root
        else:
            return findMin(root.left, root.left.axis if root.left else currAxis, axis)
    else:
        leftMin = findMin(root.left, root.left.axis if root.left else currAxis, axis)
        rightMin = findMin(root.right, root.right.axis if root.right else currAxis, axis)
        mostMin = root
        if(rightMin and mostMin.val[axis] > rightMin.val[axis]): mostMin = rightMin
        if(leftMin and mostMin.val[axis] > leftMin.val[axis]): mostMin = leftMin
        return mostMin

def deleteNode(target, root, currAxis): ## https://www.cs.cmu.edu/~ckingsf/bioinfo-lectures/kdtrees.pdf
    if(root == None): return None
    
    ## point to delete
    if(target.val["mural_registration_id"] == root.val["mural_registration_id"]):
        if(root.right):
            minObj = findMin(root.right, root.right.axis, currAxis)
            root.val = minObj.val
            root.right = deleteNode(minObj, root.right, root.right.axis)
        elif(root.left):
            minObj = findMin(root.left, root.left.axis, currAxis)
            root.val = minObj.val
            ## swap left and right subtrees of the node that's being deleted
            root.right = deleteNode(minObj, root.left, root.left.axis)
            root.left = None
        else: ## leaf node (no right or left node)
            root = None

    
    ## still need to search for point
    elif target.val[currAxis] == root.val[currAxis]: ## check both sides
        prevLeft = root.left
        root.left = deleteNode(target, root.left, root.left.axis if root.left else currAxis)
        if(root.left == prevLeft):
            root.right = deleteNode(target, root.right, root.right.axis if root.right else currAxis)

    elif target.val[currAxis] < root.val[currAxis]:
        root.left = deleteNode(target, root.left, root.left.axis if root.left else currAxis)

    else:
        root.right = deleteNode(target, root.right, root.right.axis if root.right else currAxis)

    return root

def getNearest(root, target): ## https://www.youtube.com/watch?v=Glp7THUpGow
    ## (visual of exception: https://drive.google.com/file/d/1IbuNENnNDhXTKFEe0Dm7rOzIozFRNBmp/view?usp=sharing)
    if(root == None): return None
    nextBranch = None
    otherBranch = None
    
    axis = root.axis
    if(root.val[axis] < target[axis]):
        nextBranch = root.right
        otherBranch = root.left
    else:
        nextBranch = root.left
        otherBranch = root.right
    
    temp = getNearest(nextBranch, target)
    best = root if (temp == None or abs(target[axis]-temp.val[axis]) > abs(target[axis]-root.val[axis])) else temp
    
    distToBest = target[axis]-best.val[axis]
    distToCurrIndex = target[axis]-root.val[axis]
    
    if(distToBest * distToBest >= distToCurrIndex * distToCurrIndex):
        temp = getNearest(otherBranch, target)
        best = root if (temp == None or abs(target[axis]-temp.val[axis]) > abs(target[axis]-root.val[axis])) else temp

    return best ## return object of nearest coordinate


def kNearestKDTree(root, target, k):
    """KD-tree optimized k-NN search"""
    results = []
    
    def search(node):
        if not node:
            return
        
        # Calculate distance to current node
        dist = haversine(
            (node.val['latitude'], node.val['longitude']), 
            (target['latitude'], target['longitude']), 
            unit=Unit.MILES
        )
        
        # Add to results if we have room or if closer than existing
        if len(results) < k:
            results.append((dist, node.val))
            results.sort(key=lambda x: x[0])  # Keep sorted
        elif dist < results[-1][0]:  # Replace farthest if closer
            results[-1] = (dist, node.val)
            results.sort(key=lambda x: x[0])
        
        # KD-tree traversal logic (pruning based on axis)
        axis = node.axis
        if target[axis] < node.val[axis]:
            search(node.left)
            # Check if we need to search other side
            if len(results) < k or abs(target[axis] - node.val[axis]) < results[-1][0]:
                search(node.right)
        else:
            search(node.right)
            if len(results) < k or abs(target[axis] - node.val[axis]) < results[-1][0]:
                search(node.left)
    
    search(root)
    return [point for dist, point in results]

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