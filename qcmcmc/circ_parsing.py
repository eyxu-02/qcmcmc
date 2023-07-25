import qforte as qf
from qforte import *
import scipy as sp
import numpy as np

def to_qf_circ( compressed_circ ):
        
        qf_circ = qf.Circuit()
        for i in compressed_circ:
            if len(i[1]) == 1:
                qf_circ.add_gate(qf.gate(i[0], i[1][0],i[1][0], i[2]))
            elif len(i[1]) == 2:
                qf_circ.add_gate(qf.gate(i[0], i[1][0],i[1][1]))
        
        return qf_circ

def compress_circ( circ ):
    circuit = copy.deepcopy(circ)
    compressed_circ = []
    while len(circuit) > 0:
        if len(circuit[0][0]) == 1 and circuit[0][0] != "I":
            signs = []
            gate_indices = []
            gate_type = circuit[0][0][1:]
            qubit_index = circuit[0][1]
            signs.append(circuit[0][0][:1])

            for j in range(1,len(circuit)):

                if circuit[j][0] != "I":
                    if circuit[j][1] == qubit_index:
                        if circuit[j][0][1:] == gate_type:
                            signs.append(circuit[j][0][:1])
                            gate_indices.append(j)
                        else:
                            break
            for j in reversed(gate_indices):
                circuit.pop(j)
            
            compressed_circ.append(compress_rotations( gate_type,qubit_index,signs ))
            circuit.pop(0)

        elif len(circuit[0][0]) == 2:
            compressed_circ.append(circuit[0])
            circuit.pop(0)
        else:
            circuit.pop(0)

    return compressed_circ

def compress_rotations(self, gate_type, index, signs):

    angle = 0

    for i in range(len(signs)):
        if signs[i] == "+":
            angle += np.pi/(2**i)
        elif signs[i] == "-":
            angle -= np.pi/(2**i)

    gate = [gate_type, index, angle]

    return gate

