import argparse
import math
import os
from collections import Counter


def max_word_occurance(document_or_set):
    if isinstance(document_or_set, set):
        return max([max_word_occurance(d) for d in document_or_set])
    elif isinstance(document_or_set, Counter):
        most_common = document_or_set.most_common(1)
        if not most_common:
            return 0
        return most_common[0][1]
    else:
        return 0


def tf(term, document):

    '''calculate term frequency
    let count_t be the number of times t occurs in document d
    let max_w be the maximum number of times any word occurs in document d
    tf(t,d) = count_t / max_w
    '''

    return document[term] / float(max_word_occurance(document))


def idf(term, document_set):
    '''calculate inverse document frequency
    let N be the number of documents, i.e., |D|
    let count be the number of documents term t appears in (ranges from 1 to N)
    idf(t,D) = log_e(N/count)
    '''

    num_docs_with_term = sum([1 for d in document_set.itervalues() if term in d])
    return math.log(len(document_set) / float(num_docs_with_term))


def tfidf(term, document, document_set):
    '''calculate term frequency-inverse document frequency
    tfidf(t,d,D) = tf(t,d)*idf(t,D)
    '''

    return tf(term, document) * idf(term, document_set)


def get_word_count_from_string(input_string):
    alpha_filter = lambda w: ''.join([c.lower() for c in w if c.isalpha()])
    return Counter([alpha_filter(w) for w in input_string.split() if w])


def print_tfidf_csv(files):
    pass


def get_tfidf_from_files(files):
    document_set = {}
    for file_name in files:
        doc_name = os.path.basename(file_name.strip(".txt"))
        with open(file_name) as fd:
            document_set[doc_name] = get_word_count_from_string(fd.read())

    #terms = list(set([t for
                      #d in document_set.itervalues() for
                      #t in d.iterkeys()]))

    tfidf_set = {n: {t: tfidf(t, d, document_set) for
                     t in d.keys()} for
                 n, d in document_set.iteritems()}

    return tfidf_set


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    tfidf_set = get_tfidf_from_files(args.files)
