#Author: Suki Sahota
import math
from random import randrange

class HMMDecode:

    @staticmethod
    def process_token(prev, curr, unknown_token, idx_of_token, \
        transition_matrix, emission_matrix):

        #Outerloop iterates over current column of probabilities
        for idx, prob in enumerate(curr):

            term3 = 0 #Placeholder value
            token_idx = -1

            if unknown_token in idx_of_token:
                #Known word
                token_idx = idx_of_token[unknown_token]
                term3 = emission_matrix[idx+1][token_idx] #TERM 3 FROM EQN

            #Innerloop iterates over previous column of probabilities
            for index, old_prob in enumerate(prev):
                term1 = prev[index] #TERM 1 FROM EQN
                '''
                if 0 == term1:
                    #Previous markov chain is 0; no need to continue it
                    continue
                '''

                #Already smothed from hmm-model
                term2 = transition_matrix[index+1][idx+1] #TERM 2 from EQN

                #Adds logarithms to prevent underflow error
                cur_prob = term1 + term2 + term3

                #Update curr column
                if 0 != cur_prob:
                    curr[idx] = cur_prob

    @staticmethod
    def find_tag_with_max(curr, pos_by_idx):
        max_idx = -1
        max_prob = -math.inf
        for idx, prob in enumerate(curr, start=1):
            if 0 != prob and prob > max_prob:
                max_idx = idx
                max_prob = prob

        #Returns random PoS if all probabilities are tied for 0
        return pos_by_idx[max_idx] \
            if -1 != max_idx \
            else pos_by_idx[randrange(1, len(pos_by_idx) + 1)]

###Driver code###
import sys
from hmmlearn import HMMLearn

input_path = sys.argv[1]

idx_of_pos = dict()
pos_by_idx = dict()
idx_of_token = dict()
token_by_idx = dict()

num_data = -1

transition_matrix = []
emission_matrix = []

with open('hmmmodel.txt', 'r') as model_file:
    num_data = model_file.readline().strip()
    #Read in empty line
    model_file.readline()

    #Read in transition matrix column headers
    for idx, pos in enumerate(model_file.readline().split(), start=1):
        pos = pos[:-1]
        idx_of_pos[pos] = idx
        pos_by_idx[idx] = pos

    #Read in contents of transition matrix
    #head = [next(model_file) for x in range(len(idx_of_pos))]
    for i in range(len(idx_of_pos)+1): #Also reads in first row for 'IV'
        transition_matrix.append([])
        line = next(model_file).strip()
        for raw_probability in line.split():
            probability = raw_probability.strip()
            probability = float(probability[:-1])
            transition_matrix[len(transition_matrix)-1].append(probability)

    #Read in empty line
    model_file.readline()

    #Read in emission matrix column headers
    for idx, token in enumerate(model_file.readline().split(), start=1):
        token = token[:-1]
        idx_of_token[token] = idx
        token_by_idx[idx-1] = token

    #Read in contents of emission matrix
    for i in range(len(idx_of_pos)+1): #lso reads in first row for 'IV'
        emission_matrix.append([])
        line = next(model_file).strip()
        for raw_probability in line.split():
            probability = raw_probability.strip()
            probability = float(probability[:-1])
            emission_matrix[len(emission_matrix)-1].append(probability)

    assert not model_file.readline(), 'There is still more to read from file.'

#print('DEBUGGER: ')
#print(idx_of_pos)
#print(transition_matrix)
#print(idx_of_token)
#print(emission_matrix)

with open('hmmoutput.txt', 'w') as outfile:
    #Maybe probability of 1 can be zero in the beginning??
    prev = [1] * len(idx_of_pos)
    curr = [-math.inf] * len(idx_of_pos)
    with open(input_path, 'r') as f:
        for line in f:
            for unknown_token in line.split():
                HMMDecode.process_token(prev, curr, unknown_token, \
                    idx_of_token, transition_matrix, emission_matrix)

                my_tag = HMMDecode.find_tag_with_max(curr, pos_by_idx)
                print(unknown_token + '/' + my_tag, file=outfile, end=' ')

                #Update prev with curr's values
                prev = curr

            print(file=outfile)
#################
