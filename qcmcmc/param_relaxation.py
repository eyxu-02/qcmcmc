import qforte as qf
from qforte import *
import scipy as sp
import numpy as np
import csv
from qcmcmc.circ_parsing import *

def relax_params(circ, mcmc):

    circ = compress_circ(circ)
    circ = to_qf_circ(circ)

    init_guess = circ.get_parameters()

    #print iteration 0 stuff

    iteration = 1

    results = sp.optimize.minimize(param_optimization, init_guess, args = (circ,mcmc.H[0], mcmc.nqubits), method = "BFGS", callback = printBFGSiter)
    return results

def printBFGSiter(BFGSx_n):     
    global iteration
    with open("output3.csv", mode="a",newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow([iteration,  param_optimization(BFGSx_n)])

    iteration += 1

def param_optimization(params, circ, H, nqubits):
    
    circ.set_parameters(params)
    qcomp = qf.Computer(nqubits)
    qcomp.apply_circuit(circ)
    return np.real(qcomp.direct_op_exp_val(H))