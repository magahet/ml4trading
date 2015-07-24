import sys

alpha_filter = lambda w: ''.join([c.lower() for c in w if c.isalpha()])
words = [alpha_filter(w) for l in sys.stdin for w in l.split()]
num_translator = lambda w: ''.join([format(ord(c) - 97, '02') for c in w])
print '\n'.join([num_translator(w) for w in words])
