#Author: Suki Sahota
import math

class HMMLearn:

    @staticmethod
    def grab_token_tag(token_tag):
        #Find last forward slash in token_tag and use as separator
        separator = token_tag.rindex('/')
        token = token_tag[0:separator]
        tag = token_tag[separator+1:]
        return token, tag

    @staticmethod
    def add_pos_to_matrices(trans_mat, emiss_mat, prev_tag_idx, tag_idx):
        #Add new tag to trans matrix
        trans_mat.append([0] * len(trans_mat[0]))
        #DEBUG: print(f'tag_idx is {tag_idx} and len(trans_mat)-1 is {len(trans_mat)-1}')
        assert len(trans_mat)-1 == tag_idx, \
            'Oops, added tag to matrix incorrect'
        HMMLearn.add_column_to_matrix(trans_mat)
        #Assert tag_idx is in bounds and newest index
        assert len(trans_mat[0])-1 == tag_idx, \
            'Oops, added tag to matix incorrect'

        #Add to emiss matrix
        emiss_mat.append([0] * len(emiss_mat[0]))
        assert len(emiss_mat)-1 == tag_idx, \
            'Oops, added token to matrix incorrect'

    @staticmethod
    def add_token_to_matrix(emiss_mat, token_idx):
        #Add column to matrix
        HMMLearn.add_column_to_matrix(emiss_mat)
        assert len(emiss_mat[0])-1 == token_idx, \
            'Oops, added token to matrix incorrect'

    @staticmethod
    def add_column_to_matrix(my_matrix):
        #Add column to matrix
        for row in my_matrix:
            row.append(0)

    @staticmethod
    def print_col_headings(file, my_dict):
        file.write('\n')
        for idx, key in enumerate(my_dict, start=1):
            assert idx == my_dict[key], \
                'Oh-no, my dictionary got reordered somehow'
            print(key, file=file, end=', ')
        file.write('\n')

    @staticmethod
    def print_body_matrix(file, num_data, my_matrix):
        for row in my_matrix:
            #DEBUG: print('Entering a new row in matrix!!!')
            if row != my_matrix[0]: file.write('\n')
            for column in row:
                #DEBUG: print(f'The size of this row is {len(row)} and column is {column}')
                probability = math.log(column+1 / num_data)
                print(probability, file=file, end=', ')
        file.write('\n')

###Driver code###
import sys

input_path = sys.argv[1]

parts_of_speech = dict() #key:pos, value:idx in matrices
tokens = dict() #key:token, value:idx in emission matrix
num_data = 0

#First row in each matrix is "initialization" vector
transition_matrix = [[0]]
emission_matrix = [[0]] #IV is meaningless here

with open(input_path, 'r') as f:
    prev_tag = None
    for line in f:
        for token_tag in line.split():
            token, tag = HMMLearn.grab_token_tag(token_tag.strip())

            prev_tag_idx = 0 if prev_tag == None else parts_of_speech[prev_tag]

            tag_idx = -1
            if tag in parts_of_speech:
                tag_idx = parts_of_speech[tag]
            else:
                tag_idx = len(emission_matrix)
                parts_of_speech[tag] = tag_idx
                HMMLearn.add_pos_to_matrices(
                    transition_matrix, emission_matrix, prev_tag_idx, tag_idx)

            token_idx = -1
            if token in tokens:
                token_idx = tokens[token]
            else:
                token_idx = len(emission_matrix[0])
                tokens[token] = token_idx
                HMMLearn.add_token_to_matrix(emission_matrix, token_idx)

            #Increment count of tag
            transition_matrix[prev_tag_idx][tag_idx] += 1
            #Increment count of token
            emission_matrix[tag_idx][token_idx] += 1
            num_data = num_data + 1

            #Update prev_tag with current tag
            prev_tag = tag

#Write to model
with open('hmmmodel.txt', 'w') as model_file:
    #Print num of data
    print(num_data, file=model_file)

    #Print transition matrix
    HMMLearn.print_col_headings(model_file, parts_of_speech)
    #Print body of matrix
    HMMLearn.print_body_matrix(model_file, num_data, transition_matrix)

    #Print emission matrix
    HMMLearn.print_col_headings(model_file, tokens)
    #Print body of matrix
    HMMLearn.print_body_matrix(model_file, num_data, emission_matrix)
#################
