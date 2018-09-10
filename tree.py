"""Creating a tree"""

import re
import graphVisual
import velocity
import escaped_mass

class Node:
    """A node of a tree
        Value :=    first entry: target
                    second entry: impactor
                    third entry: time of impact"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(value)

class BinarySearchTree:
    """A Binary Search Tree. Built for easy traversal, the BST initializes an empty
    node by creating two empty BST as subtrees."""

    def __init__(self, root):
        if root is None:
            self._root = None
            self._left = None
            self._right = None
        else:
            self._root = root
            self._left = BinarySearchTree(None)
            self._right = BinarySearchTree(None)

    def add_node(self, BST, side):
        """Ability to add nodes"""
        if side == "right":
            self._right = BST
        if side == "left":
            self._left = BST

def data(filename):
    with open(filename) as f:
        content = f.readlines()[3:]
    content = [x.strip() for x in content]
    return content

def extract_data(line): #Use regex to parse the datafile
    # For .emb files
    pattern = re.compile(r"""(?P<time>\d+[.]\d+[e][+\-]\d*)\s*
                             (?P<EMBmass>\d+[.]\d+[e][+\-]?\d*)\s*
                             (?P<name>\w+\d+)\s*
                             (?P<IMPmass>\d+[.]\d+[e][+\-]?\d*)\s*
                             (?P<R>\d+[.]\d+[e][+\-]?\d*)\s*
                          """, re.VERBOSE)
    match = pattern.match(line)
    if match is not None:
        time = float(match.group("time"))
        EMBmass = float(match.group("EMBmass"))
        IMPmass = float(match.group("IMPmass"))
        impactor = match.group("name")
        Radius = float(match.group("R"))
    else:
        time = []; EMBmass = []; IMPmass = []; impactor = []; Radius = []

    return time, EMBmass, IMPmass, impactor, Radius


def build_children(targ, impp, tim, last_collision, targ_radius, M_targ, M_imp):
    tree_list = []
    content = data(impp+".emb")

    time = []
    EMBmass = []
    IMPmass = []
    impactor = []
    Radius = []
    for i in range(len(content)):
        t, emb, imp, name, r = extract_data(content[i])
        if t != []:
            time.append(t)
            EMBmass.append(emb)
            IMPmass.append(imp)
            impactor.append(name)
            Radius.append(r)

    if len(time) == 0: # There are no earlier collisions
        # If this was the last collision of the embryo that this embryo will
        # collide with next, create a node with two leafs
        if last_collision:
            targ_mass = escaped_mass.find_init_mass(targ)
            imp_mass = escaped_mass.find_init_mass_no_collision(targ)
            first_coll_targ_BST = BinarySearchTree(Node([targ, None, 0, (targ_mass, 0), None]))
            first_coll_imp_BST = BinarySearchTree(Node([impp, None, 0, (imp_mass, 0), None]))
            vel_rel = velocity.compute_relative_velocity(targ, tim, targ_radius, M_targ+M_imp)
            M_real, sigma = escaped_mass.compute_real_mass(targ, tim, impp)
            first_coll_BST = BinarySearchTree(Node([targ, impp, vel_rel, (M_real, sigma), tim]))
            first_coll_BST.add_node(first_coll_targ_BST, "left")
            first_coll_BST.add_node(first_coll_imp_BST, "right")
            tree_list += [first_coll_BST]

        # However, if that is not the case, one of the children will keep having
        # collisions at an earlier time. It is still the first collision of the
        # current embryo
        else:
            vel_rel = velocity.compute_relative_velocity(targ, tim, targ_radius, M_targ+M_imp)
            M_real, sigma = escaped_mass.compute_real_mass(targ, tim, impp)
            first_coll_BST = BinarySearchTree(Node([targ, impp, vel_rel, (M_real, sigma), tim]))
            impp_mass = escaped_mass.find_init_mass_no_collision(targ)
            lone_node_BST = BinarySearchTree(Node([impp, None, 0, (impp_mass, 0), None]))
            first_coll_BST.add_node(lone_node_BST, "left")
            tree_list += [first_coll_BST]

    # The impactor is the first and only impactor of the current embryo
    elif len(time) == 1:
        # Recurse into the only child (impactor)
        tree_list += build_children(impp, impactor[0], time[0], True, Radius[0], EMBmass[0], IMPmass[0])
        vel_rel = velocity.compute_relative_velocity(targ, tim, targ_radius, M_targ+M_imp)
        M_real, sigma = escaped_mass.compute_real_mass(targ, tim, impp)
        parent_coll_BST = BinarySearchTree(Node([targ, impp, vel_rel, (M_real, sigma), tim]))

        # If this is the first collision of the target, its leaf node goes here
        if last_collision:
            targ_mass = find_init_mass(targ)
            coll_targ_BST = BinarySearchTree(Node([targ, None, 0, (targ_mass, 0), None]))
            parent_coll_BST.add_node(coll_targ_BST, "left")
        tree_list += [parent_coll_BST]

    else:
        # In case of multiple impacts, we need to figure out when the embryo
        # begun its journey. This is done by recursing through every child
        # and building their own binary collision trees.
        children = []
        for i in range(len(impactor) - 1, 0, -1):
            tree_list += build_children(impp, impactor[i], time[i], False, Radius[i], EMBmass[i], IMPmass[i])
        tree_list += build_children(impp, impactor[0], time[0], True, Radius[0], EMBmass[0], IMPmass[0])


        vel_rel = velocity.compute_relative_velocity(targ, tim, targ_radius, M_targ+M_imp)
        M_real, sigma = escaped_mass.compute_real_mass(targ, tim, impp)
        parent_BST = BinarySearchTree(Node([targ, impp, vel_rel, (M_real, sigma), tim]))
        # Exact same case as when there is only 1 impactor left
        if last_collision:
            targ_mass = find_init_mass(targ)
            coll_targ_BST = BinarySearchTree(Node([targ, None, 0, (targ_mass, 0), None]))
            parent_BST.add_node(coll_targ_BST, "left")
        tree_list += [parent_BST]
    return tree_list

def sort_BST_list(BST_list):
    """A very simple sorting algorithm in O(n^2)."""
    sorted_list = []
    while len(BST_list) > 0:
        index = 0
        max_index = 0
        max = BST_list[0]
        while index < len(BST_list):
            if BST_list[index]._root.value[-1] > max._root.value[-1]:
                max = BST_list[index]
                max_index = index
            index += 1
        sorted_list.append(max)
        del BST_list[max_index]
    return sorted_list

def connect_BST(BST_list):
    # Note that before connecting all the collisions together, the list of
    # collisions is sorted by collision time. This means that collisions can
    # only be connected to collisions at later positions within the list.
    # Collisions due to two vanilla embryos do not need any connecting since
    # they would already have been created during the creation of the BSTs.
    i = 0
    while i < len(BST_list):
        # The case if the BST has one node and no children.
        # This means that this collision was a result of two other collisions.
        if (BST_list[i]._left._root is None) and (BST_list[i]._right._root is None):
            iter = 1
            first_index = 0
            found_first = False
            targ = BST_list[i]._root.value[0]; impactor = BST_list[i]._root.value[1]
            # Find the first possible child collision
            while iter < len(BST_list) and not found_first:
                same_target = (BST_list[i + iter]._root.value[0] == targ)
                same_impactor = (BST_list[i + iter]._root.value[1] == impactor)
                same_opp_targ = (BST_list[i + iter]._root.value[0] == impactor)
                same_opp_imp = (BST_list[i + iter]._root.value[1] == targ)
                if same_target or same_impactor or same_opp_imp or same_opp_targ:
                    BST_list[i].add_node(BST_list[i + iter], "left")
                    found_first = True
                    first_index = i + iter
                iter += 1

            iter = 1
            found_second = False
            # Find the second possible child collision
            while iter < len(BST_list) and not found_second:
                if i + iter != first_index:
                    same_target = (BST_list[i + iter]._root.value[0] == targ)
                    same_impactor = (BST_list[i + iter]._root.value[1] == impactor)
                    same_opp_targ = (BST_list[i + iter]._root.value[0] == impactor)
                    same_opp_imp = (BST_list[i + iter]._root.value[1] == targ)
                    if same_target or same_impactor or same_opp_imp or same_opp_targ:
                        BST_list[i].add_node(BST_list[i + iter], "right")
                        found_second = True
                iter += 1

        # It is possible that the collision is a product of a vanilla embryo and
        # an other collision.
        elif (BST_list[i]._left._root is None):
            iter = 1
            found_first = False
            targ = BST_list[i]._root.value[0]; impactor = BST_list[i]._root.value[1]
            while iter < len(BST_list) and not found_first:
                same_target = (BST_list[i + iter]._root.value[0] == targ)
                same_impactor = (BST_list[i + iter]._root.value[1] == impactor)
                same_opp_targ = (BST_list[i + iter]._root.value[0] == impactor)
                same_opp_imp = (BST_list[i + iter]._root.value[1] == targ)
                if same_target or same_impactor or same_opp_imp or same_opp_targ:
                    BST_list[i].add_node(BST_list[i + iter], "left")
                    found_first = True
                iter += 1

        # Same as the last elif statement, but mirrored
        elif (BST_list[i]._right._root is None):
            iter = 1
            found_first = False
            targ = BST_list[i]._root.value[0]; impactor = BST_list[i]._root.value[1]
            while iter < len(BST_list) and not found_first:
                same_target = (BST_list[i + iter]._root.value[0] == targ)
                same_impactor = (BST_list[i + iter]._root.value[1] == impactor)
                same_opp_targ = (BST_list[i + iter]._root.value[0] == impactor)
                same_opp_imp = (BST_list[i + iter]._root.value[1] == targ)
                if same_target or same_impactor or same_opp_imp or same_opp_targ:
                    BST_list[i].add_node(BST_list[i + iter], "right")
                    found_first = True
                iter += 1
        i += 1

#main()
def main():
    f = "EMB"
    super_tree_list = []
    Real_Mass = []
    Fake_Mass = []
    StandardDiv = []
    for i in range(0, 15):
        tree_list = []
        content = data(f+str(i)+".emb")

        time = []
        EMBmass = []
        IMPmass = []
        impactor = []
        Radius = []
        for j in range(len(content)):
            t, emb, imp, name, r = extract_data(content[j])
            time.append(t)
            EMBmass.append(emb)
            IMPmass.append(imp)
            impactor.append(name)
            Radius.append(r)

        if len(time) >= 1:
            M_real, sigma = escaped_mass.compute_real_mass(f+str(i), time[-1], impactor[-1])
            Real_Mass.append(M_real)
            StandardDiv.append(sigma)
            Fake_Mass.append((EMBmass[-1] + IMPmass[-1])*1.989e30)

            vel_rel = velocity.compute_relative_velocity(f+str(i), time[-1], Radius[-1], EMBmass[-1]+IMPmass[-1])
            final_collision = Node([f+str(i), impactor[-1], vel_rel, (M_real, sigma), time[-1]])
            rootBST = BinarySearchTree(final_collision)

            children = []
            for j in range(len(impactor) - 1, 0, -1):
                tree_list += build_children(f+str(i), impactor[j], time[j], False, Radius[j], EMBmass[j], IMPmass[j])

            tree_list += build_children(f+str(i), impactor[0], time[0], True, Radius[0], EMBmass[0], IMPmass[0])

            if tree_list[-1]._root.value[1] is None:
                rootBST.add_node(tree_list[-1], "left")
                del tree_list[-1]
                tree_list.append(rootBST)

            sorted_tree_list = sort_BST_list(tree_list)
            connect_BST(sorted_tree_list)
            super_tree_list.append((sorted_tree_list[0], f+str(i)))
    return super_tree_list, Real_Mass, Fake_Mass, StandardDiv

if __name__ == "__main__":
    super_tree_list, Real_Mass, Fake_Mass, std = main()
    for i in range(len(super_tree_list)):
        graphVisual.main(super_tree_list[i][0], super_tree_list[i][1], Real_Mass[i], Fake_Mass[i], std[i])
