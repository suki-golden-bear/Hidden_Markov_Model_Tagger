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
        #Add PoS row to trans matrix
        trans_mat.append([0] * len(trans_mat[0]))
        #Assert tag_idx is in bounds and has newest/last index
        assert len(trans_mat)-1 == tag_idx, \
            'Oops, added tag to transition matrix incorrect'

        #Add PoS column to trans matrix
        HMMLearn.add_column_to_matrix(trans_mat)
        #Assert tag_idx is in bounds and has newest/last index
        assert len(trans_mat[0])-1 == tag_idx, \
            'Oops, added tag to transition matix incorrect'

        #Add PoS row to emiss matrix
        emiss_mat.append([0] * len(emiss_mat[0]))
        #Assert tag_idx is in bounds and has newest/last index
        assert len(emiss_mat)-1 == tag_idx, \
            'Oops, added token to emission matrix incorrect'

    @staticmethod
    def add_token_to_matrix(emiss_mat, token_idx):
        #Add PoS column to emiss matrix
        HMMLearn.add_column_to_matrix(emiss_mat)
        #Assert token_idx is in bounds and has newest/last index
        assert len(emiss_mat[0])-1 == token_idx, \
            'Oops, added token to emission matrix incorrect'

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
    def print_body_matrix(file, num_data, my_matrix, is_trans_mat):
        for row in my_matrix:
            if row != my_matrix[0]: file.write('\n')
            for column in row:
                probability = column
                if True == is_trans_mat:
                    #One-smoothing only for states, not observations
                    probability += 1
                probability = column / num_data
                if 0 != probability:
                    probabilty = math.log(probability)
                print(probability, file=file, end=', ')
        file.write('\n')

###Driver code###
if '__name__' == '__main__':
    import sys
    
    input_path = sys.argv[1]
    
    parts_of_speech = dict() #key:pos, value:idx in matrices
    tokens = dict() #key:token, value:idx in emission matrix
    num_data = 0
    
    #First row and column in each matrix is "initialization" vector
    #ROWS: Parts of Speech, COLUMNS: Parts of Speech
    transition_matrix = [[0]]
    #ROWS: Parts of Speech, COLUMNS: observations
    emission_matrix = [[0]]
    
    with open(input_path, 'r') as f:
        prev_tag = None
        for line in f:
            for token_tag in line.split():
                token, tag = HMMLearn.grab_token_tag(token_tag.strip())
    
                prev_tag_idx = 0
                if prev_tag != None:
                    prev_tag_idx = parts_of_speech[prev_tag]
    
                tag_idx = -1
                if tag in parts_of_speech:
                    tag_idx = parts_of_speech[tag]
                else:
                    tag_idx = len(transition_matrix)
                    parts_of_speech[tag] = tag_idx
                    HMMLearn.add_pos_to_matrices(
                        transition_matrix, emission_matrix, \
                        prev_tag_idx, tag_idx)
    
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
        HMMLearn.print_body_matrix(
            model_file, num_data, transition_matrix, True)
    
        #Print emission matrix
        HMMLearn.print_col_headings(model_file, tokens)
        #Print body of matrix
        HMMLearn.print_body_matrix(
            model_file, num_data, emission_matrix, False)
#################
