"""Follow the Gabriel process."""

from numpy import sin, pi, linspace, log10, sqrt
from random import random, randint
import re
import escaped_mass

# constants
G = 6.67408e-11

def data2(filename):
    with open(filename) as f:
        content = f.readlines()[2:]
    content = [x.strip() for x in content]
    return content

def extract_data2(line): #Use regex to parse the datafile
    pattern = re.compile(r"""\s*(?P<Ncol>\d+)\s*
                             (?P<Impactor>\w*\d+)\s*
                             (?P<time>\d+[.]?\d*)\s*
                             (?P<vel>\d+[.]?\d*)\s*
                             (?P<dmin>\d+[.]?\d*?)\s*
                             (?P<xp>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<yp>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<zp>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<vxp>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<vyp>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<vzp>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<xi>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<yi>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                             (?P<zi>[\-]?\d+[.]?\d+[E]?[+\-]?\d*)\s*
                         """, re.VERBOSE)
    match = pattern.match(line)
    time = float(match.group("time"))
    vel = float(match.group("vel"))
    dmin = float(match.group("dmin"))
    impactor = match.group("Impactor")
    xp, yp = float(match.group("xp")), float(match.group("yp"))
    zp = float(match.group("zp"))
    xi, yi = float(match.group("xi")), float(match.group("yi"))
    zi = float(match.group("zi"))
    p = [xp, yp, zp]; i = [xi, yi, zi]

    return time, vel, impactor, p, i

def reduced_mass(M_t, M_i):
    return (M_t*M_i)/(M_t + M_i)

def escape_velocity(M_t, M_i, R):
    return ((2.*G*(M_t + M_i))/R)**0.5

def binding_energy(M, R): # No layers, const density
    return -(3./5.)*(G*M**2/R)

def col_energy(mu, v_i):
    return 0.5*mu*v_i**2

def radius(M, rho):
    return ((3./4.)*(M/(1000.*pi*rho)))**(1./3.)

def distance(p1, p2):
    rad = 0
    for i in range(len(p1)):
        rad += (p1[i]*1.494e11 - p2[i]*1.494e11)**2
    return sqrt(rad)

def radius2(dist, M1, M2):
    mass_ratio = M1/M2
    R2 = mass_ratio**(-1./3.)*(dist - 1)
    R1 = dist - R2
    return R1, R2

#main()
def compute_real_mass(M_targ, M_imp, filename_of_targ, imp): #SI units only pls
    cnt = 0
    total = 0
    N = 100
    x = linspace(0, pi/2, N)
    y = sin(x)
    rho = 3.0

    # Load the data
    # need mass and radii of target and impactor
    content2 = data2(filename_of_targ+".colls")

    p1 = []
    p2 = []
    for i in range(len(content2)):
        t, vel, impactor, p1val, p2val = extract_data2(content2[i])
        if imp == impactor:
            print(impactor)
            v_i = vel
            p1.append(p1val)
            p2.append(p2val)
            time = t

    print("time = "+str(time))
    dist = distance(p1[0], p2[0])
    R_targ, R_imp = radius2(dist, M_targ, M_imp)

    EMBmass, IMPmass = escaped_mass.find_collision_mass(filename_of_targ, time)
    R_targ_sim, R_imp_sim = radius2(dist, EMBmass, IMPmass)
    v_esc_sim = escape_velocity(EMBmass, IMPmass, R_targ_sim+R_imp_sim)

    total += 1
    M_LR_lst = []
    M_run_lst = []
    v_esc = escape_velocity(M_targ, M_imp, R_imp + R_targ)
    v_i_sim = v_esc_sim * (v_i/v_esc)

    print("Targ Filename: "+filename_of_targ+"\t Impactor: "+imp)
    print("v_i_sim: "+str(v_i_sim)+"\t v_esc_sim: "+
            str(v_esc_sim)+"\t v_i: "+str(v_i)+"\t v_esc: "+str(v_esc))
    print("EMBmass: "+str(EMBmass)+"\t IMPmass: "+str(IMPmass)+"\n"+
            "M_targ: "+str(M_targ)+"\t M_imp: "+str(M_imp))

    for i in range(100):
        # Step 0
        theta_imp = y[int(random()*100)]*180/pi + 0.001
        M_tot = M_targ + M_imp

        # Step 1
        mu = reduced_mass(M_targ, M_imp)

        # Step 2
        U_Gi = binding_energy(M_imp, R_imp)
        U_Gt = binding_energy(M_targ, R_targ)
        U_G = U_Gi + U_Gt + G*((M_targ*M_imp)/(R_targ+R_imp))

        # Step 3
        E_k = col_energy(mu, v_i_sim)
        gamma = M_imp/M_targ

        # Step 4
        theta_HnR = -28.82*log10(gamma) + 10.57
        v_HnR = (18.67/theta_imp + 0.83)*v_esc_sim

        if (theta_imp > theta_HnR) and (v_i_sim > v_HnR):
            xi_jump = 1. - 1./(gamma * (theta_imp - theta_HnR - 10.76))
            M_LR_star = M_tot - xi_jump*M_imp
            M_run_star = M_tot - M_LR_star
            HnR = True
            cnt += 1
        else:
            M_LR_star = M_tot
            HnR = False

        # Step 5
        alpha = 8.734e-5*(gamma**0.83)*(theta_imp**3.455) + 3.438
        E_k_star = -alpha*U_G
        M_LR = M_LR_star*(1. - E_k/E_k_star)
        M_LR_lst.append(M_LR)
        #print("M_LR: "+str(M_LR)+"\t ")

        M_run = 0
        # Step 6
        if HnR:
            M_run = M_run_star*(1. - E_k/E_k_star)

        # Step 7
        if HnR:
            M_esc = M_tot - M_LR - M_run
        else:
            M_esc = M_tot - M_LR

        M_run_lst.append(M_run)

    mean_LR = sum(M_LR_lst) / len(M_LR_lst)
    mean_run = sum(M_run_lst) / len(M_run_lst)

    summing_LR = 0
    for i in range(len(M_LR_lst)):
        summing_LR += (M_LR_lst[i] - mean_LR)**2

    summing_run = 0
    for i in range(len(M_run_lst)):
        summing_run += (M_run_lst[i] - mean_run)**2

    sigma_LR = sqrt(summing_LR/len(M_LR_lst))
    sigma_run = sqrt(summing_run/len(M_run_lst))

    return [mean_LR, sigma_LR], [mean_run, sigma_run], EMBmass, IMPmass, HnR
