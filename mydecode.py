#Author: Suki Sahota
import math
from random import randrange

class HMMDecode:

    @staticmethod
    def process_token(prob_mat, back_pnts, unknown_token, idx_of_token, \
        transition_matrix, emission_matrix, trellises):

        curr = len(prob_mat) - 1 #Index of last column in prob_mat
        prev = curr - 1          #Index of second to last column in prob_mat

        #Outerloop iterates over each trellis (chart out each trellis path)
          #trellis_num is position in trellises array.
          #trellis_idx holds index in prob_mat 
            #where this trellis previously left off.
        for trellis_num, trellis_idx in enumerate(trellises):

            #__EQN__: cur_prob = prev prob + trans prob + emission prob
              #trans matrix is PoS by PoS
              #emiss matrix is PoS by Token

            #To keep track of which back pointer wins out
            winning_bck_pntr = -1
            winning_bck_pcnt = 0.0
            winning_cur_idx = -1

            #Innerloop iterates on curr column based on which trellis we are on
            for idx in range(len(prob_mat(curr))):

                term1 = prob_mat[prev][trellis_idx] #TERM 1 FROM EQN

                #Already smothed from hmm-model
                term2 = \
                    transition_matrix[trellis_idx+1][idx+1] #TERM 2 from EQN

                term3 = 0 #Placeholder value
                token_idx = -1
                if unknown_token in idx_of_token:
                    #Known word
                    token_idx = idx_of_token[unknown_token]
                    term3 = emission_matrix[idx+1][token_idx] #TERM 3 FROM EQN

                #Adds logarithms to prevent underflow error
                cur_prob = term1 + term2 + term3

                #Update winning percentage
                if cur_prob != 0 and cur_prob > winning_bck_pcnt:
                    winning_bck_pcnt = cur_prob
                    winning_bck_pntr = trellis_idx
                    winning_cur_idx = idx

            #Used during back propagation as next part of algorithm
            back_pnts[curr][winning_cur_idx] = winning_bck_pntr
            trellises[trellis_num] = winning_cur_idx #Used for next iteration

    @staticmethod
    def back_propagation(line, back_pntrs, \
        winningest_trellis_idx, pos_by_idx):
        outline = ''
        for token in reversed(line.split()):
            #Grab PoS
            my_tag = pos_by_idx[winningest_trellis_idx]
            winningest_trellis_idx = back_pntrs[:, -1][winningest_trellis_idx]

            #Generate token/PoS tag
            outline = token + '/' + my_tag + outline

            #Shrink back pointers matrix by one column
            back_pntrs = back_pntrs[:-1]
        
        return outline

    @staticmethod
    def print_output(outfile, final_output):
        outline for outline in final_output:
            print(outline, file=outfile, end='')

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
    for i in range(len(idx_of_pos)+1): #Also reads in first row for 'IV'
        emission_matrix.append([])
        line = next(model_file).strip()
        for raw_probability in line.split():
            probability = raw_probability.strip()
            probability = float(probability[:-1])
            assert probability >= 0, 'Oops, emission matrix has neg prob'
            emission_matrix[len(emission_matrix)-1].append(probability)

    assert not model_file.readline(), 'There is still more to read from file.'

with open('hmmoutput.txt', 'w') as outfile:
    prob_mat =  [[1] * len(idx_of_pos)]
    back_pnts = [[0] * len(idx_of_pos)]
    #Initially, each trellis is unique
    trellises = [i for i in range(len(idx_of_pos))] #0 index'ed

    with open(input_path, 'r') as f:
        for line in f:
            for unknown_token in line.split():
                #Create new column in each matrix
                prob_mat.append([1] * len(idx_of_pos))
                back_pnts.append([1] * len(idx_of_pos))

                HMMDecode.process_token(prob_mat, back_pnts, unknown_token, \
                    idx_of_token, transition_matrix, emission_matrix, \
                    trellises)

            #print(file=outfile) #New line I think

    final_output = []
    winningest_trellis_idx = max(prob_mat[:, -1])

    with open(input_path, 'r') as f:
        for line in reversed(f):
            #Back propagation one line at a time
            outline = HMMDecode.back_propagation(line, back_pnts, \
                winningest_trellis_idx, pos_by_idx)

            final_output = outline.append('\n' + final_output)

    HMMDecode.print_output(outfile, final_output)

#################
