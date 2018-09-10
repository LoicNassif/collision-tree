"""Velocity computations"""

import re
from numpy import sqrt

def data(filename):
    with open(filename) as f:
        content = f.readlines()[2:]
    content = [x.strip() for x in content]
    return content

def data2(filename):
    with open(filename) as f:
        content = f.readlines()[3:]
    content = [x.strip() for x in content]
    return content

def extract_data(line): #Use regex to parse the datafile
    # for .colls files
    pattern = re.compile(r"""(?P<Ncol>\d*)\s*
                             (?P<Impactor>\w+\d+)\s*
                             (?P<time>\d*[.]?\d*)\s*
                             (?P<vel_imp>\d*[.]?\d*)\s*
                          """, re.VERBOSE)
    match = pattern.match(line)
    if match is not None:
        time = float(match.group("time"))
        vel_imp = float(match.group("vel_imp"))
        impactor = match.group("Impactor")
    else:
        time = []; vel_imp = []; impactor = []

    return time, vel_imp, impactor

def extract_data2(line): #Use regex to parse the datafile
    # for .dat files
    pattern = re.compile(r"""(?P<time>\d+[.]\d+[e][+\-]\d*)\s*
                             (?P<mass>\d+[.]\d+[e][+\-]\d*)\s*
                             (?P<vel_esc>\d+[.]\d+[e][+\-]\d*)\s*
                          """, re.VERBOSE)
    match = pattern.match(line)
    if match is not None:
        time = float(match.group("time"))
        vel_esc = float(match.group("vel_esc"))
    else:
        time = []; vel_esc = []

    return time, vel_esc

def escape_velocity(M, R):
    G = 6.673e-11
    return sqrt(2*G*(M*1.989e30)/R)

def relative_velocity(v_dist, v_esc_dist, v_esc_sphere):
    return (v_dist**2 - v_esc_dist**2 + v_esc_sphere**2)**(0.5)

def find_vel(t, time_lst, vel): #Maybe Use
    for i in range(len(time_lst)):
        if t-5 <= time_lst[i] <= t+5:
            return vel[i]
    return False

def load_colls_files(filename):
    content = data(filename)

    time = []; vel_imp = []; impactor = []
    for i in range(len(content)):
        t, vel, name = extract_data(content[i])
        if t != []:
            time.append(t)
            vel_imp.append(vel)
            impactor.append(name)

    return time, vel_imp, impactor

def load_dat_files(filename):
    content = data2(filename)

    time = []; vel_esc = []
    for i in range(len(content)):
        t, vel = extract_data2(content[i])
        if t != []:
            time.append(t)
            vel_esc.append(vel)

    return time, vel_esc

def compute_relative_velocity(filename, time, radius, total_mass):
    time_colls, vel_imp, impactor_list = load_colls_files(filename+".colls")
    time_esc, vel_esc_list = load_dat_files(filename+".dat")

    v_esc = find_vel(time, time_esc, vel_esc_list)
    v_imp = find_vel(time, time_colls, vel_imp)
    v_esc_sphere = escape_velocity(total_mass, radius)

    return sqrt(v_imp**2 - v_esc**2 + v_esc_sphere**2)/v_esc
