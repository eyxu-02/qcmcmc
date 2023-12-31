import qforte as qf
from qforte import *
import scipy as sp
import numpy as np
from qcmcmc.circ_parsing import *

def cost_function( circuit, args ):

    components = args[0]
    weights = args[1]
    component_args = args[2]

    cost = 0
    for i in range(len(components)):
        component = components[i]
        cost += component(circuit, component_args[i]) * weights[i]

    return cost

def energy( circuit, component_args):

    nqubits = component_args[0]
    hamiltonian = component_args[1]
    circ = compress_circ(circuit)
    #revert to_qf_circ argument to circ
    qf_circ = to_qf_circ(circ)
    qcomp = qf.Computer(nqubits)
    qcomp.apply_circuit(qf_circ)

    return np.real(qcomp.direct_op_exp_val(hamiltonian))

def depth( circ, component_args ):

    nqubits = component_args[0]
    circuit = compress_circ(circ)
    circuit = circ

    qubit_stack = []
    depth = 0

    for i in range(nqubits):
        qubit_stack.append(0)

    for i in circuit:
        if i[0] != "I":
            if i[0] == "CNOT":
                if qubit_stack[i[1][0]] > qubit_stack[i[1][1]]:
                    qubit_stack[i[1][1]] = qubit_stack[i[1][0]]
                    qubit_stack[i[1][0]] += 1
                    qubit_stack[i[1][1]] += 1
                else:
                    qubit_stack[i[1][0]] = qubit_stack[i[1][1]]
                    qubit_stack[i[1][0]] += 1
                    qubit_stack[i[1][1]] += 1
            else:
                qubit_stack[i[1][0]] += 1
    
    depth += max(qubit_stack)

    return depth

def fidelity( circuit, component_args):

    nqubits = component_args[0]
    ref = component_args[1]
    circ = compress_circ(circuit)
    qf_circ = to_qf_circ(circ)

    overlap = qf.compute_operator_matrix_element(nqubits, ref, qf_circ, None)

    fidelity = overlap**2

    return -fidelity