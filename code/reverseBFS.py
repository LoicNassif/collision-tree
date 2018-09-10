"""A reverse breadth first search to compute the corrected mass of the tree."""
from queue import Queue
import gabriel

def BFS(BST, depth):
    level = 0
    q = Queue()
    visited_set = set()

    #Init
    root = BST
    depth[level] = [root]
    root._root.value[3] = (None, None)
    q.put((root, level))

    while not q.empty():
        subtree, level = q.get()
        if (subtree._left._root is not None) and (subtree._right._root is not None):

            if subtree._left._root in visited_set:
                continue
            else:
                if subtree._left._left._root is not None:
                    subtree._left._root.value[3] = (None, None)
                if level+1 in depth:
                    depth[level+1] += [subtree._left]
                else:
                    depth[level+1] = [subtree._left]
                q.put((subtree._left, level+1))

            if subtree._right._root in visited_set:
                continue
            else:
                if subtree._right._left._root is not None:
                    subtree._right._root.value[3] = (None, None)
                if level+1 in depth:
                    depth[level+1] += [subtree._right]
                else:
                    depth[level+1] = [subtree._right]
                q.put((subtree._right, level+1))

        visited_set.add(subtree._root)

def compute_real_mass(BST):
    depth = {}
    BFS(BST, depth)
    for key in depth:
        max = key

    for i in range(max, -1, -1):
        print("current level = "+str(i))
        for j in range(len(depth[i])):
            print("\t"+str(depth[i][j]._root.value))
            if (depth[i][j]._left._root is None) or (depth[i][j]._right._root is None):
                depth[i][j]._root.value.append(0)
                mass = depth[i][j]._root.value[3][0]
                print("mass None = "+str(mass is None))
                depth[i][j]._root.value.append(mass)
                continue
            else:
                M_targ = depth[i][j]._right._root.value[3][0]
                M_imp = depth[i][j]._left._root.value[3][0]
                print("\t\t targ = "+ str(depth[i][j]._right._root.value))
                print("\t\t imp = "+ str(depth[i][j]._left._root.value))
                print()
                M_LR, M_run, EMBmass, IMPmass = gabriel.compute_real_mass(M_targ, M_imp,
                                                    depth[i][j]._root.value[0],
                                                    depth[i][j]._root.value[1])
                print()
                print("\t\t targ from parent = "+depth[i][j]._root.value[0])
                print("\t\t imp form parent = "+depth[i][j]._root.value[1])
                print()
                print("\t M_LR = "+str(M_LR[0]) + " std = " + str(M_LR[1]))
                print()
                depth[i][j]._root.value[3] = (M_LR[0], M_LR[1])
                depth[i][j]._root.value.append(M_run[0])
                print("MRun = " + str(M_run[0] is None))
                print("Mtot = " + str(EMBmass + IMPmass is None))
                depth[i][j]._root.value.append(EMBmass + IMPmass)

    return depth
