from random import randrange
from research.paths import output_path

RANK_LIMIT = 16014219505238849250
with open(output_path("RN100M.txt"), "w") as wf:
    for i in range(100_000_000):
        wf.write(str(randrange(0, RANK_LIMIT)) + "\n")
