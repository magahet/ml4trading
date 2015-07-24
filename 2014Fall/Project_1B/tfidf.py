import argparse

def max_word_occurance(document_or_set):
    if isinstance(document_or_set, set):
        return max([max_word_occurance(d) for d in document_or_set
    elif isinstance(document_or_set, Counter):
        most_common = document_or_set.most_common(1)
        if not most_common:
            return 0
        return most_common[1]
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
    
    num_docs_with_term = len([1 for d in document_set if d[term]])
    return math.log(len(document_set) / float(num_docs_with_term))
    

def tfidf(term, document, document_set):
    '''calculate term frequency–inverse document frequency
    tfidf(t,d,D) = tf(t,d)*idf(t,D)
    '''

    return tf(term, document) * idf(term, document_set)
    
    
def get_word_count_from_string(input_string):
    alpha_filter = lambda w: ''.join([c.lower() for c in w if c.isalpha()])
    return Counter([alpha_filter(w) for w in input_string.split()])
    

def print_tfidf_csv(files):
    document_set = {}
    for file in files:
        doc_name = file.strip(".txt")
        with open(file) as fd:
            document_set[doc_name] = get_word_count_from_string(fd.read())
    
    terms = set([t for d in document_set.itervalues() for t in d.iterkeys()])
    
    print terms
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()