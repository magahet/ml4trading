import sys

grouper = lambda l: ['{}{}'.format(a, b) for a, b in zip(*([iter(l)] * 2))]
alpha_translator = lambda l: ''.join([chr(int(n) + 97) for n in grouper(l)])
print '\n'.join([alpha_translator(l.strip()) for l in sys.stdin.readlines()])
