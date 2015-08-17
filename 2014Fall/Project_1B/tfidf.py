import argparse
import math
import os
import csv
import sys
from collections import Counter


def max_word_occurance(document_or_set):
    if isinstance(document_or_set, (set, list, tuple)):
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
    return Counter([w for w in
                    [alpha_filter(w) for
                     w in input_string.split() if w] if w])


def get_tfidf_from_files(files):
    document_set = {}
    for file_name in files:
        doc_name = os.path.basename(file_name.strip(".txt"))
        with open(file_name) as fd:
            document_set[doc_name] = get_word_count_from_string(fd.read())

    return {n: {t: tfidf(t, d, document_set) for
                t in d.keys()} for
            n, d in document_set.iteritems()}


def print_tfidf_table(tfidf_set):
    ordered_fieldnames = ['term'] + sorted([k for k in tfidf_set.iterkeys() if k])
    terms = sorted(list(set([t for d in tfidf_set.itervalues() for
                             t in d.iterkeys()])))
    dw = csv.DictWriter(sys.stdout, delimiter=',', fieldnames=ordered_fieldnames)
    dw.writeheader()
    for term in terms:
        row = {n: '{0:0.4f}'.format(d.get(term, 0.0)) for n, d in tfidf_set.iteritems()}
        row['term'] = term
        dw.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    print_tfidf_table(get_tfidf_from_files(args.files))
