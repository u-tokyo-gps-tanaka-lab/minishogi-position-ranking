from random import randrange

RANK_LIMIT = 16014219505238849250
with open('RN10K.txt', 'w') as wf:
    for i in range(10_000):
        wf.write(str(randrange(0, RANK_LIMIT)) + '\n')