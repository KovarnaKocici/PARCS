# import gmpy2
from Pyro4 import expose
import re

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited")

    def solve(self):
        print("Job Started")
        print("Workers %d" % len(self.workers))

        input_ = self.read_input()
        # map
        mapped = []
        i = 0
        
        for line in input_:
            mapped.append(self.workers[i % len(self.workers)].mymap(i, input_[i]))
            i += 1

        # reduce
        inverted_index = self.myreduce(mapped)

        sortKey = lambda x: sum([pair[1] for pair in x[1]])
        inverted_index_sorted = sorted(list(inverted_index.items()), key = sortKey)[::-1]

        # output
        self.write_output(inverted_index_sorted)

        print("Job Finished")

    @staticmethod
    @expose
    def mymap(file, text):
        print(file)
        print(text)
        return parse_text(file, text)

    @staticmethod
    @expose
    def myreduce(mapped):
        print("reduce")
        output = {}
        for i in range(len(mapped)):
            for key, value in mapped[i].value.items():
                if key in output:
                    output[key] += value
                else:
                    output[key] = value
        print("reduce done")
        if '' in output:
            del output['']
        print(output)
        return output

    def read_input(self):
        print("Started reading input")
        f = open(self.input_file_name, 'r')
        texts = f.read().split(".") # Create a list containing all lines
        f.close()
        print("Finished reading input")
        return texts

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        for key, value in output:
            f.write(key + ' : ' + str(value) + '\n')
        # f.write('\n')
        f.close()
        print("output done")

def split_text(text):
    clean_text = re.sub(r'\W', ' ', text.lower())
    super_clean_text = re.sub(r' +', ' ', clean_text)
    return super_clean_text.split(' ')

def word_count(splitted_text, word):
    occur = 0
    for word_in_text in splitted_text:
        if word_in_text == word:
            occur += 1
    return  occur

def parse_text(filename, text):#(filename, [(word, occurances)])
    file_word_count = dict()
    all_words = split_text(text)
    unique_words = set(all_words)
    for word in unique_words:
        file_word_count[word] = [(filename, word_count(all_words, word))]
    return file_word_count
   
