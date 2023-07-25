import qforte as qf
from qforte import *
import scipy as sp
import numpy as np
from qcmcmc.circ_parsing import *
from qcmcmc.cost_fxns import *
import csv

class MCMC:

    eq_classes = [["I"], ["+Rx","-Rx","+Ry","-Ry","+Rz","-Rz"], ["CNOT"]]

    def __init__(self, temp, num_qubits, hamiltonians, rng_seed ):
        
        self.T = temp
        self.nqubits = num_qubits
        self.H = hamiltonians
        self.rng = np.random.default_rng(rng_seed)
        
    def mcmc( self, iters, starting_circ, threshold, cost_func_args, output_file ):

        current_circ = starting_circ
        candidates = []

        for i in range(iters):
            next_circ = self.random_move(current_circ)
            current_cost = cost_function(current_circ, cost_func_args )
            next_cost = cost_function(next_circ, cost_func_args )
            cost_diff = next_cost - current_cost

            if current_cost < threshold:
                candidates.append(current_circ)
            
            with open(output_file, mode="a",newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                row = [i, depth(current_circ, [self.nqubits])]

                for j in self.H:
                    row.append( energy(current_circ, [self.nqubits, j]) )
                       
                row.append(current_circ)
                writer.writerow(row)

            if cost_diff <= 0 or self.rng.rand() < sp.special.expit(-1*cost_diff / self.T):
                current_circ = next_circ

        return candidates
            
    def opcode(self, circuit):

        indices = []

        for i in range(len(circuit)):
            if MCMC.eq_classes[1].count(circuit[i][0]) > 0:
                indices.append(i)
        
        if len(indices) > 0:
            index = self.rng.choice(indices)
            replacement = self.rng.choice(MCMC.eq_classes[1])

            if replacement != circuit[index][0]:
                circuit[index][0] = replacement
            else:
                while replacement == circuit[index][0]:
                    replacement = self.rng.choice(MCMC.eq_classes[1])
                circuit[index][0] = replacement  
        return circuit   
    
    def operand(self, circuit):
        indices = []

        for i in range(len(circuit)):
            if MCMC.eq_classes[1].count(circuit[i][0]) > 0 or MCMC.eq_classes[2].count(circuit[i][0]) > 0:
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

        rand_num = self.rng.rand()

        if rand_num < .125:
            gate.append(self.rng.choice(MCMC.eq_classes[0]))
            return gate
        elif rand_num < .875:
            gate.append(self.rng.choice(MCMC.eq_classes[1]))
            gate.append([self.rng.choice(self.nqubits)])
            return gate
        else:
            gate.append(self.rng.choice(MCMC.eq_classes[2]))
            operand = [self.rng.choice(self.nqubits), self.rng.choice(self.nqubits)]
            if operand[0] != operand[1]:
                gate.append(operand)
            else:
                while operand[0] == operand[1]:
                    operand = [self.rng.choice(self.nqubits), self.rng.choice(self.nqubits)]
                gate.append(operand)
            return gate
        
    def random_move(self, circuit):

        rand_num = self.rng.rand()
        if rand_num < .5:
            circ = self.operand(circuit)
        elif rand_num < .66:
            circ = self.opcode(circuit)
        elif rand_num < .82:
            circ = self.swap(circuit)
        else:
            circ = self.instruction(circuit)

        return circ
