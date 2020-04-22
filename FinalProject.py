# Final Project
# Copied from tsp.py given by the professor

#
# Helper functions for the Traveling Salesman Problem
#

import math
import random
import time


# returns true if lst is a permutation of the ints 1 to len(lst), and false
# otherwise
def is_good_perm(lst):
    return sorted(lst) == list(range(1, len(lst) + 1))


# returns the distance between points (x1,y1) and (x2,y2)
def dist(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx * dx + dy * dy)


# c1 and c2 are integer names of cities, randing from 1 to len(city_locs)
# city_locs is a list of pairs of coordinates (e.g. from load_city_locs)
def city_dist(c1, c2, city_locs):
    return dist(city_locs[c1 - 1][0], city_locs[c1 - 1][1],
                city_locs[c2 - 1][0], city_locs[c2 - 1][1])


# city_perm is a list of 1 or more city names
# city_locs is a list of pairs of coordinates for every city
def total_dist(city_perm, city_locs):
    assert is_good_perm(city_perm), f'city_perm={city_perm}'
    n = len(city_perm)
    total = city_dist(city_perm[0], city_perm[n - 1], city_locs)
    for i in range(1, n):
        total += city_dist(city_perm[i - 1], city_perm[i], city_locs)
    return total


def str_lst(lst):
    return ', '.join(str(i) for i in lst)


def first_n(n, lst):
    result = str_lst(lst[:n])
    if len(lst) > n:
        result += ' ...'
    return result


def rand_perm(n):
    result = list(range(1, n + 1))
    random.shuffle(result)
    return result


# return the shortest of max_iter random permutations
def rand_best(fname, max_iter):
    start_time = time.time()
    city_locs = load_city_locs(fname)
    n = len(city_locs)

    best = rand_perm(n)
    best_score = total_dist(best, city_locs)
    print(f'New best perm ({n}): {best}')
    print(f'              Score: {best_score}\n')
    assert is_good_perm(best)

    curr = best[:]
    curr_score = total_dist(curr, city_locs)
    assert is_good_perm(best)
    assert is_good_perm(curr)

    for i in range(max_iter):
        if curr_score < best_score:
            best = curr
            best_score = curr_score
            print(f'New best perm ({n}): {first_n(5, best)}')
            print(f'              Score: {best_score}\n')
        random.shuffle(curr)
        curr_score = total_dist(curr, city_locs)

    print(f'After {max_iter} random tries, this is the best tour:')
    print(best)
    print(f'score = {best_score}')
    elapsed_time = time.time() - start_time
    print(f'\nElapsed time (in seconds): {elapsed_time}s')
    fileGenerator(best, best_score, 0, max_iter, elapsed_time)


def do_rand_swap(lst):
    n = len(lst)
    i, j = random.randrange(n), random.randrange(n)
    lst[i], lst[j] = lst[j], lst[i]  # swap lst[i] and lst[j]


# Starts with a random population. Then repeats the following:
#  - copy unchanged the best permutation into the next generation
#  - add "mutated" copies to the next generation, where a mutation is a swap
#    of a random pair of cities
#
# This is a kind of local search, where a randomly chosen set of "children" of
# the best permutation are put into the next generation.
def mutate_search(fname, max_iter, pop_size):
    start_time = time.time()
    city_locs = load_city_locs(fname)
    n = len(city_locs)
    curr_gen = [rand_perm(n) for i in range(pop_size)]
    curr_gen = [(total_dist(p, city_locs), p) for p in curr_gen]
    curr_gen.sort()
    assert len(curr_gen) == pop_size

    print(f'mutate_search("{fname}", max_iter={max_iter}, pop_size={pop_size}) ...')
    for i in range(max_iter):
        # put best permutation from curr_gen into next generation unchanged
        best_curr_gen = curr_gen[0][1]
        next_gen = [best_curr_gen]

        # the rest of the next generation is filled with random swap-mutations
        # of best_curr_gen
        for j in range(pop_size - 1):
            perm = best_curr_gen[:]  # make a copy of best_curr_gen
            do_rand_swap(perm)  # randomly swap two cities
            next_gen.append(perm)  # add it to next_gen

        # create the next generation of (score, permutations) pairs
        assert len(next_gen) == pop_size
        curr_gen = [(total_dist(p, city_locs), p) for p in next_gen]
        curr_gen.sort()

    print(f'... mutate_search("{fname}", max_iter={max_iter}, pop_size={pop_size})')
    print()
    print(f'After {max_iter} generations of {pop_size} permutations, the best is:')
    print(f'score = {curr_gen[0][0]}')
    print(curr_gen[0][1])
    assert is_good_perm(curr_gen[0][1])
    elapsed_time = time.time() - start_time
    print(f'\nElapsed time (in seconds): {elapsed_time}s')
    fileGenerator(curr_gen[0][1], curr_gen[0][0], pop_size, max_iter, elapsed_time)


#
# The following explanation of PMX is from this paper:
#
# https://www.researchgate.net/publication/245746380_Genetic_Algorithm_Solution_of_the_TSP_Avoiding_Special_Crossover_and_Mutation
#
# Parents are s=5713642 and t=4627315, and | is a randomly chosen crossover
# point:
#
#    s=571|3642
#    t=462|7315
#
# Two offspring will be created by the crossover.
#
# First offspring: make a copy of s (call it s'), and write s' above t (t
# won't change). Then go through the first 3 cities of s and swap them (in s')
# with the city underneath in t. For example:
#
#       swap        swap        swap
#       +-----+     +---+       +----+
#       |     |     |   |       |    |
#   s'= 571|3642   471|3652   461|3752   462|3751
#   t = 462|7315   462|7315   462|7315   462|7315
#
# So 4627315 is the first offspring.
#
# The second offspring is created similarly, but this time s stays the same
# and a copy t' of t is made:
#
#   s = 571|3642   571|3642   571|3642   571|3642
#   t'= 462|7315   562|7314   572|6314   571|6324
#       |      |    |  |        |   |
#       +------+    +--+        +---+
#       swap        swap        swap
#
# Thus 5716324 is the second offspring.
#
def pmx(s, t):
    assert is_good_perm(s)
    assert is_good_perm(t)
    assert len(s) == len(t)
    n = len(s)

    # choose crossover point at random
    c = random.randrange(1, n - 1)  # c is index of last element of left part

    # first offspring
    first = s[:]
    i = 0
    while i <= c:
        j = first.index(t[i])
        first[i], first[j] = first[j], first[i]
        i += 1

    # second offspring
    second = t[:]
    i = 0
    while i <= c:
        j = second.index(s[i])
        second[i], second[j] = second[j], second[i]
        i += 1

    assert is_good_perm(first)
    assert is_good_perm(second)

    return first, second


# Each generation, pairs of permutations from the top 50% of the population
# are "bred" to create the next generation.
def crossover_search(fname, max_iter, pop_size):
    start_time = time.time()
    city_locs = load_city_locs(fname)
    n = len(city_locs)
    curr_gen = [rand_perm(n) for i in range(pop_size)]
    curr_gen = [(total_dist(p, city_locs), p) for p in curr_gen]
    curr_gen.sort()
    assert len(curr_gen) == pop_size

    print(f'crossover_search("{fname}", max_iter={max_iter}, pop_size={pop_size}) ...')
    for i in range(max_iter):
        # copy the top 50% of the population to the next generation, and for the rest randomly
        # cross-breed pairs
        top_half = [p[1] for p in curr_gen[:int(n / 2)]]
        next_gen = top_half[:]
        while len(next_gen) < pop_size:
            s = random.choice(top_half)
            t = random.choice(top_half)
            first, second = pmx(s, t)
            next_gen.append(first)
            next_gen.append(second)

        next_gen = next_gen[:pop_size]

        # create the next generation of (score, permutations) pairs
        assert len(next_gen) == pop_size
        curr_gen = [(total_dist(p, city_locs), p) for p in next_gen]
        curr_gen.sort()

    print(f'... crossover_search("{fname}", max_iter={max_iter}, pop_size={pop_size})')
    print()
    print(f'After {max_iter} generations of {pop_size} permutations, the best is:')
    print(f'score = {curr_gen[0][0]}')
    print(curr_gen[0][1])
    assert is_good_perm(curr_gen[0][1])
    elapsed_time = time.time() - start_time
    print(f'\nElapsed time (in seconds): {elapsed_time}s')
    fileGenerator(curr_gen[0][1], curr_gen[0][0], pop_size, max_iter, elapsed_time)


"""____________________________________________READ/WRITE FILE_________________________________________________"""


# returns a list of pairs of coordinates, where the first pair is the location
# of the first city, the second pair is the location of second city, and so on
def load_city_locs(fname):
    f = open(fname)
    result = []
    for line in f:
        data = [int(s) for s in line.split(' ')]
        result.append(tuple(data[1:]))
    return result


def fileGenerator(result, score, pop_size, max_itr, elapsed_time):
    f = open("cities1000_ladha_mutate_9.txt", "w")
    line = ""
    for obj in result:
        line += str(obj) + " "
    f.write(line)
    f.write(f"\n\nScore: {score}")
    f.write(f'\nPop Size: {pop_size}')
    f.write(f'\nMax itr: {max_itr}')
    f.write(f'\nTime: {elapsed_time}')
    f.close()


"""____________________________________________RUN PROGRAM_________________________________________________"""


def run():
    fname = input("Enter the file name with extension: ")

    # rand_best(fname, 100000)
    mutate_search(fname, max_iter=10000, pop_size=750)
    # crossover_search(fname, max_iter=10000, pop_size=500)


if __name__ == '__main__':
    run()
