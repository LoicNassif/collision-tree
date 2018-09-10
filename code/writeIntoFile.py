"""Write into a file instead of displaying visuals"""
import tree
import reverseBFS

def create_file(filename, M_LR_lst, level_lst, M_run_lst, total_mass_lst, HnR_lst):
    line1 = "\t\t"+filename[:-4]+"\t"+"Embryo collisions"+"\n"
    line2 = ("M_LR"+"\t\t\t\t"+"level"+"\t\t\t\t"+"M_run"+"\t\t\t"+"Total Mass"+"\t\t\t"+"HnR"+"\n")
    line3 = "---------------------------------------------------------------------"+"\n"

    f = open(filename, "w+")
    f.write(line1); f.write(line2); f.write(line3);
    for i in range(len(M_LR_lst)):
        f.write(str("{0:.8e}".format(M_LR_lst[i]))+"\t\t"+
                str("{0:.8e}".format(level_lst[i]))+"\t\t"+
                str("{0:.8e}".format(M_run_lst[i]))+"\t\t"+
                str("{0:.8e}".format(total_mass_lst[i]))+"\t\t"+
                HnR_lst[i]+"\n")
    f.close

def main():
    BST, _, __, ___ = tree.main()
    for k in range(len(BST)):
        M_LR_lst = []
        level_lst = []
        total_mass_lst = []
        M_run_lst = []
        HnR_lst = []
        depth = reverseBFS.compute_real_mass(BST[k][0])
        lvl = len(depth)
        for i in range(len(depth)):
            for j in range(len(depth[i])):
                M_LR_lst.append(depth[i][j]._root.value[3][0])
                total_mass_lst.append(depth[i][j]._root.value[6])
                M_run_lst.append(depth[i][j]._root.value[5])
                level_lst.append(lvl)
                HnR_lst.append(depth[i][j]._root.value[7])
            lvl -= 1

        print("MLR_lst: "+ str(M_LR_lst))
        print("levels: "+ str(level_lst))
        print("total_mass_lst: "+ str(total_mass_lst))
        print("Mrun_lst: "+str(M_run_lst))
        create_file("corrected_collisions"+str(k)+".tru", M_LR_lst, level_lst, M_run_lst, total_mass_lst, HnR_lst)

if __name__ == "__main__":
    main()
