test:
	time ./testqlearner.py testworlds/world01.csv -i 500; \
	time ./testqlearner.py testworlds/world02.csv -i 500
profile:
	python -m cProfile -s cumtime testqlearner.py testworlds/world01.csv -i 1000 -d 10 > out
