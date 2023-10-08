import qforte as qf
from qforte import *
from scipy.optimize import fmin_bfgs
import numpy as np
import csv
from qcmcmc.circ_parsing import *
import sys
qcmcmc = sys.modules[__name__]

def relax_params (circ, mcmc, output_file):
    global iteration
    global output_file_name

    output_file_name = output_file

    circ = compress_circ(circ)
    circ = to_qf_circ(circ)

    init_guess = circ.get_parameters()
    qcomp = qf.Computer(mcmc.nqubits)
    qcomp.apply_circuit(circ)

    
    with open(output_file, mode="a",newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        row = [0,  np.real(qcomp.direct_op_exp_val(mcmc.H[0]))] + list(init_guess)
        writer.writerow(row)
    
    iteration = 1
    results = sp.optimize.minimize(param_opt_obj_fun, init_guess, args = (circ,mcmc.H[0], mcmc.nqubits), method = 'bfgs', callback = BFGSxk)

    with open(output_file, mode="a",newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        row = ["After optimization",  results.fun] + list(results.x)
        writer.writerow(row)

    return results

def BFGSxk( intermediate_result ):     
    global iteration
    global output_file_name

    with open(output_file_name, mode="a",newline='') as csvfile:
        
        row = [iteration,  intermediate_result.fun] + list(intermediate_result.x)
        print(row)
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(row)

    iteration += 1

def param_opt_obj_fun(params, circ, H, nqubits):
    
    circ.set_parameters(params)
    qcomp = qf.Computer(nqubits)
    qcomp.apply_circuit(circ)
    return np.real(qcomp.direct_op_exp_val(H))