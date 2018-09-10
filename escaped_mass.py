"""The escaped mass"""

import re
from numpy import sqrt
import gabriel

def data(filename):
    with open(filename) as f:
        content = f.readlines()[2:]
    content = [x.strip() for x in content]
    return content

def extract_data(line): #Use regex to parse the datafile
    # for .esc files
    pattern = re.compile(r"""(?P<time>\d+[.]\d+[e][+\-]\d*)\s*
                             (?P<EMBmass>\d+[.]\d+[e][+\-]\d*)\s*
                             (?P<IMPmass>\d+[.]\d+[e][+\-]\d*)\s*
                             (?P<Mesc>\d+[.]\d+[e][+\-]\d*)\s*
                             (?P<HnR>\w+)\s*
                             (?P<theta_imp>\d+[.]\d+[e][+\-]\d*)\s*
                          """, re.VERBOSE)
    match = pattern.match(line)
    if match is not None:
        time = float(match.group("time"))
        EMBmass = float(match.group("EMBmass"))
        IMPmass = float(match.group("IMPmass"))
        Mesc = float(match.group("Mesc"))
        HnR = match.group("HnR")
        theta_imp = float(match.group("theta_imp"))
    else:
        time = []; EMBmass = []; IMPmass = []; Mesc = []
        HnR = []; theta_imp = []

    return time, EMBmass, IMPmass, Mesc, HnR, theta_imp

def load_esc_files(filename):
    content = data(filename)
    time = []; EMBmass = []; IMPmass = []
    M_esc = []; HnR = []; theta_imp = []
    for i in range(len(content)):
        t, emb, imp, m, hit, theta = extract_data(content[i])
        if t != []:
            time.append(t)
            EMBmass.append(emb)
            IMPmass.append(imp)
            M_esc.append(m)
            HnR.append(hit)
            theta_imp.append(theta)

    return time, EMBmass, IMPmass, M_esc, HnR, theta_imp

def find_collision_mass(filename, t):
    time, EMBmass, IMPmass, M_esc, HnR, theta_imp = load_esc_files(filename+".esc"+str(1))
    time_index = 0
    print("time to aim: "+str(t))
    for j in range(len(time)):
        print("current time: "+str(time[j]))
        if t - 5e5 <= time[j] <= t + 5e5:
            print("time found: "+str(time[j]))
            time_index = j
    return EMBmass[time_index], IMPmass[time_index]

def compute_real_mass(filename, t, imp):
    real_mass_list = []

    time, EMBmass, IMPmass, M_esc, HnR, theta_imp = load_esc_files(filename+".esc"+str(1))

    time_index = 0
    for j in range(len(time)):
        if t - 5e5 <= time[j] <= t + 5e5:
            time_index = j

    M_LR, M_run, _, __ = gabriel.compute_real_mass(EMBmass[time_index], IMPmass[time_index], filename, imp)

    return [M_LR[0], M_LR[1]]

def find_init_mass(filename):
    EMBmass_list = []
    for i in range(5):
        time, EMBmass, a, b, c, d = load_esc_files(filename+".esc"+str(1))
        EMBmass_list.append(EMBmass[0])

    return sum(EMBmass_list)/len(EMBmass_list)

def find_init_mass_no_collision(filename):
    IMPmass_list = []
    for i in range(5):
        time, EMBmass, IMPmass, b, c, d = load_esc_files(filename+".esc"+str(1))
        IMPmass_list.append(IMPmass[0])

    return sum(IMPmass_list)/len(IMPmass_list)
