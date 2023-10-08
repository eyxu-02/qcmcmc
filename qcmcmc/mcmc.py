import qforte as qf
from qforte import *
import scipy as sp
import numpy as np
from qcmcmc.circ_parsing import *
from qcmcmc.cost_fxns import *
import csv

class MCMC:

    def __init__(self, temp, num_qubits, hamiltonians, rng_seed, eq_classes):
        
        self.T = temp
        self.nqubits = num_qubits
        self.H = hamiltonians
        self.rng = np.random.default_rng(rng_seed)
        self.eq_classes = []
        for i in eq_classes:
            self.eq_classes.append(MCMC.get_eq_class(i))
        self.all_gates = []
        for i in self.eq_classes:
            for j in i:
                self.all_gates.append(j)

    def get_eq_class(i):
        if i == "Identity":
            return ["I"]
        elif i == "HST":
            return ["H","S","T"]
        elif i == "Rotations":
            return ["+Rx","-Rx","+Ry","-Ry","+Rz","-Rz"]
        elif i == "CNOT":
            return ["CNOT"]
        
    def mcmc( self, iters, starting_circ, threshold, cost_func_args, output_file ):

        current_circ = starting_circ
        candidates = []

        print("Iter: Depth: H_Energy: Ha_Energy: Hb_Energy: ", flush=True)

        with open(output_file, mode="a",newline='') as csvfile:

            for i in range(iters):
                next_circ = self.random_move(current_circ)
                current_cost = cost_function(current_circ, cost_func_args )
                next_cost = cost_function(next_circ, cost_func_args )
                cost_diff = next_cost - current_cost

                if current_cost < threshold:
                    candidates.append(current_circ)
                if i == iters - 1 and len(cost_func_args[0] > 1):
                    candidates.append(current_circ)              

                writer = csv.writer(csvfile, delimiter=',')
                row = [i, depth(current_circ, [self.nqubits])]

                for j in self.H:
                    row.append( energy(current_circ, [self.nqubits, j]) )
                
                string = ""
                for i in row:
                    string += f"{i} "

                print(string, flush=True)

                row.append(current_circ)
                writer.writerow(row)
            
                if len(candidates) > 0:
                    break
                    
                if cost_diff <= 0 or self.rng.random() < sp.special.expit(-1*cost_diff / self.T):
                    current_circ = next_circ

        return candidates
            
    def opcode(self, circuit):

        indices = []

        for i in range(len(circuit)):
            if circuit[i][0] != "CNOT" and circuit[i][0] != "I":
                indices.append(i)
        
        if len(indices) > 0:
            index = self.rng.choice(indices)
            replacement = self.rng.choice(self.all_gates)

            while replacement == "CNOT" or replacement == "I" or replacement == circuit[index][0]:
                replacement = self.rng.choice(self.all_gates)

            circuit[index][0] = replacement

        return circuit   
    
    def operand(self, circuit):
        indices = []

        for i in range(len(circuit)):
            if circuit[i][0] != "I":
                indices.append(i)
        
        if len(indices) > 0:
            index = self.rng.choice(indices)
            replacement = []
            for i in range( len(circuit[index][1])):
                replacement.append( self.rng.choice(self.nqubits))
            
            if len(replacement) == 1:
                circuit[index][1] = replacement
            elif len(replacement) == 2:
                if replacement[0] != replacement[1]:
                    circuit[index][1] = replacement
                else: 
                    while replacement[0] == replacement[1]:
                        replacement = []
                        for i in range(2):
                            replacement.append( self.rng.choice(self.nqubits))
                    circuit[index][1] = replacement
        return circuit
    
    def swap(self, circuit):
        swap = []
        for i in range(2):
            swap.append( self.rng.choice(len(circuit)))
        
        if swap[0] != swap[1]:
            temp = circuit[swap[0]]
            circuit[swap[0]] = circuit[swap[1]]
            circuit[swap[1]] = temp
        else:
            while swap[0] == swap[1]:
                swap = []
                for i in range(2):
                    swap.append( self.rng.choice(len(circuit)))
            temp = circuit[swap[0]]
            circuit[swap[0]] = circuit[swap[1]]
            circuit[swap[1]] = temp

        return circuit

    
    def instruction(self, circuit):


        index = self.rng.choice(len(circuit))
        circuit[index] = self.generate_random_gate()

        return circuit


    def generate_random_gate(self):

        gate = []

        rand_num = self.rng.random()

        if rand_num < .125:
            gate.append("I")
            return gate
        else:
            gate.append(self.rng.choice(self.all_gates))

            if gate[0] == "CNOT":
                operand = [self.rng.choice(self.nqubits), self.rng.choice(self.nqubits)]
                if operand[0] != operand[1]:
                    gate.append(operand)
                else:
                    while operand[0] == operand[1]:
                        operand = [self.rng.choice(self.nqubits), self.rng.choice(self.nqubits)]
                    gate.append(operand)
            else:
                gate.append([self.rng.choice(self.nqubits)])

            return gate
        
    def random_move(self, circ):

        circuit = copy.deepcopy(circ)

        rand_num = self.rng.random()
        if rand_num < .5:
            circ = self.operand(circuit)
        elif rand_num < .66:
            circ = self.opcode(circuit)
        elif rand_num < .82:
            circ = self.swap(circuit)
        else:
            circ = self.instruction(circuit)

        return circuit
