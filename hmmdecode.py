#Author: Suki Sahota
import math

class HMMDecode:

    @staticmethod
    def process_token(prev, curr, unknown_token, idx_of_token, \
        transition_matrix, emission_matrix):

        for idx, prob in enumerate(curr, start=1):
            #max_prob holds maximum probability for PoS under consideration
            max_prob = 0

            token_idx = -1
            if unknown_token in idx_of_token:
                token_idx = idx_of_token[unknown_token]
            else:
                #Never made this observation before during training data
                curr[idx-1] = 0
                continue

            #LEFTOFF HERE
            assert token_idx != -1, 'Oops, token_idx is -1'
            if 0 == emission_matrix[idx][token_idx]:
                #Given observation is impossible for this PoS (given training)
                curr[idx-1] = 0
                continue

            for index, old_prob in enumerate(prev, start=1):
                if 0 == prev[index-1]:
                    #Previous markov chain is 0; no need to continue it
                    continue

                term1 = math.log(prev[index-1])
                #The below probability has already been smothed from hmmmodel
                term2 = math.log(transition_matrix[index][idx])
                term3 = math.log(emission_matrix[idx][token_idx])

                cur_prob = term1 + term2 + term3
                curr[idx-1] = max(curr[idx-1], cur_prob)

    @staticmethod
    def find_tag_with_max(curr, pos_by_idx):
        max_idx = -1
        max_prob = -math.inf
        for idx, prob in enumerate(curr):
            if 0 != prob and prob > max_prob:
                max_idx = idx
                max_prob = prob

        #Returns first PoS in our records if all probabilities are 0
        return pos_by_idx[max_idx] if -1 != max_idx else pos_by_idx[1]

###Driver code###
import sys
from hmmlearn import HMMLearn

input_path = sys.argv[1]

idx_of_pos = dict()
pos_by_idx = dict()
idx_of_token = dict()
token_by_idx = dict()

num_data = -1

transition_matrix = [[]]
emission_matrix = [[]]

with open('hmmmodel.txt', 'r') as model_file:
    num_data = model_file.readline().strip()
    model_file.readline()

    #Read in transition matrix column headers
    for idx, pos in enumerate(model_file.readline(), start=1):
        idx_of_pos[pos] = idx
        pos_by_idx[idx] = pos
    #Read in contents of transition matrix
    #head = [next(model_file) for x in range(len(idx_of_pos))]
    for i in range(len(idx_of_pos)): #[0, m)
        transition_matrix.append([])
        line = next(model_file).strip()
        for raw_probability in line.split():
            probability = raw_probability[:-1]
            transition_matrix[len(transition_matrix)-1].append(probability)

    '''
    for row in transition_matrix:
        print()
        for column in row:
            print(column, end=' ')
    '''

    #Read in emission matrix column headers
    for idx, token in enumerate(model_file.readline(), start=1):
        idx_of_token[token] = idx-1
        token_by_idx[idx-1] = token
    #Read in contents of emission matrix
    for i in range(len(idx_of_token)): #[0, n)
        emission_matrix.append([])
        line = next(model_file).strip()
        for raw_probability in line.split():
            probability = raw_probability[:-1]
            emission_matrix[len(emission_matrix)-1].append(probability)

with open('hmmoutput.txt', 'w') as outfile:
    #Maybe probability of 1 can be zero in the beginning??
    prev = [0] * len(idx_of_pos)
    curr = [0] * len(idx_of_pos)
    with open(input_path, 'r') as f:
        for line in f:
            for unknown_token in line.split():
                HMMDecode.process_token(prev, curr, unknown_token, \
                    idx_of_token, transition_matrix, emission_matrix)
                my_tag = HMMDecode.find_tag_with_max(curr, pos_by_idx)
                print(unknown_token + '/' + my_tag, file=outfile, end=' ')
#################
