import argparse


def tf(term, document):
    '''calculate term frequency'''
    let count_t be the number of times t occurs in document d
    let max_w be the maximum number of times any word occurs in document d
    tf(t,d) = count_t / max_w

def idf(term, document_set):
    '''calculate inverse document frequency'''

def tfidf(term, document, document_set):
    '''calculate term frequency–inverse document frequency'''
    return tf(term, document) * idf(term, document_set)

def print_tfidf_csv(files):
    for file

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
