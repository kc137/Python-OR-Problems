import math, random, numpy as np, networkx as nx, matplotlib.pyplot as plt, time, operator, heapq, matplotlib
matplotlib.use("tkagg")


# from random import shuffle, randint, uniform, random
from deap import base, creator, tools, benchmarks, algorithms

# Start Time

start = time.time()

# Necessary Constants

colors = ["darkviolet", "limegreen", "darkorange", "magenta", "darkturquoise"]

coords_list = [(40, 50),(25, 85),(22, 75),(22, 85),(20, 80),(20, 85),(18, 75),(15, 75),(15, 80),(10, 35),(10, 40),(8, 40),(8, 45),(5, 35),(5, 45),(2, 40),(0, 40),(0, 45),(44, 5),(42, 10),(42, 15),(40, 5),(40, 15),(38, 5),(38, 15),(35, 5)]

N = len(coords_list) - 1

# distances = {n : [] for n in range(N+1)}

distance_network = np.zeros([N+1, N+1], dtype = int)

for n1 in range(N+1):
    for n2 in range(N+1):
        if n1 != n2:
            distance_network[n1][n2] = \
                round(math.hypot(coords_list[n1][0] - coords_list[n2][0], 
                           coords_list[n1][1] - coords_list[n2][1]))
        else:
            distance_network[n1][n2] = 0

# distance_network = pd.DataFrame(distances)

initial_flow = [n for n in range(1, N+1)]
random.shuffle(initial_flow)

# demands = [0, 15, 25, 34, 25, 20, 28, 17, 33, 25, 22, 19, 27, 20, 16, 21, 20]

# demands = pd.DataFrame(demands, index = [n for n in range(N+1)], columns = ["C"])

demands = np.array([0,20,30,10,40,20,20,20,10,20,30,40,20,10,10,20,20,20,20,40,10,10,40,30,10,20])

capacity = 200

service_time = 10

time_array = [(0, 240),(145, 175),(50, 80),(109, 139),(141, 171),(41, 71),(95, 125),(79, 109),(91, 121),(91, 121),(119, 149),(59, 89),(64, 94),(142, 172),(35, 65),(58, 88),(72, 102),(149, 179),(87, 117),(72, 102),(122, 152),(67, 97),(92, 122),(65, 95),(148, 178),(154, 184)]

def generate_particle(s_min, s_max):
    particle_list = [n for n in range(1, N+1)]
    random.shuffle(particle_list)
    
    particle = creator.Particle(particle_list)
    particle.speed = [random.uniform(s_min, s_max) for _ in range(N)]
    particle.smin = s_min
    particle.smax = s_max
    return particle

def update_particle(particle, best, w, phi1, phi2):
    phi1_list = (random.uniform(0, phi1) for _ in range(N))
    phi2_list = (random.uniform(0, phi1) for _ in range(N))
    # Particle Best
    speeds_1 = map(operator.mul, phi1_list, map(operator.sub, particle.best, particle))
    # Neighbourhood Best
    speeds_2 = map(operator.mul, phi2_list, map(operator.sub, best, particle))
    
    # Update Speed
    particle.speed = list(map(operator.add, map(operator.mul, particle.speed, [w]*N), 
                              map(operator.add, speeds_1, speeds_2)))
    
    modified_particle = []
    
    # Speed Limits
    for speed in particle.speed:
        if speed < particle.smin:
            modified_particle.append(particle.smin)
        elif speed > particle.smax:
            modified_particle.append(particle.smax)
        else:
            modified_particle.append(speed)
    particle[:] = convert_particle(modified_particle)
    return

# def get_fitness(particle):
#     prev = 0
#     cumu_load = 0
#     distance = 0
#     for loc in particle:
#         if cumu_load + demands[loc] <= capacity:
#             cumu_load += demands[loc]
#             distance += distance_network[prev][loc]
#             prev = loc
        
#         else:
#             cumu_load = demands[loc]
#             distance += distance_network[prev][0]
#             prev = 0
#             distance += distance_network[prev][loc]
#             prev = loc
#     distance += distance_network[0][particle[-1]]        
#     return (distance, )

def get_fitness(x):
    distance = 0
    cumu_dem = 0
    tardiness = 0
    cumu_time = 0
    routes = 1
    
    distance += distance_network[0][x[1]]
    for i in range(1, N):
        if cumu_time + distance_network[x[i-1]][x[i]] <= time_array[x[i]][1] and cumu_dem <= capacity: #  and cumu_dem <= capacity
            distance += distance_network[x[i-1]][x[i]]
            cumu_time += distance_network[x[i-1]][x[i]]
            if cumu_time < time_array[x[i]][0]:
                cumu_time = time_array[x[i]][0]
            if cumu_time > time_array[x[i]][1]:
                # tardiness += cumu_time - time_array[x[i]][1]
                cumu_time += service_time
            else:
                cumu_time += service_time
            # cumu_dem += demands[x[i]]
        else:
            distance += distance_network[x[i-1]][x[0]]
            cumu_time = time_array[x[i]][0]
            routes += 1
            if cumu_time > time_array[x[i]][1]:
                # tardiness += cumu_time - time_array[x[i]][1]
                cumu_time += service_time
            else:
                cumu_time += service_time
            distance += distance_network[x[0]][x[i]]
            # cumu_dem = demands[x[i]]
    distance += distance_network[x[-1]][x[0]]
    
    return (distance, routes)

def convert_particle(particle):
    enum_particle = [(val, idx) for idx, val in enumerate(particle)]
    heapq.heapify(enum_particle)
    validated_particle = []

    for _ in range(len(enum_particle)):
        location = heapq.heappop(enum_particle)[1]
        validated_particle.append(location + 1)

    return validated_particle

def run_pso(pop_size = 100, max_iterations = 1000, weight = 0.8, phi1 = 2, phi2 = 2, max_s = 3.0):
    creator.create("Min_Fitness", base.Fitness, weights = (-1.0, -1.0))
    creator.create("Particle", list, fitness = creator.Min_Fitness, 
                   speed = list, s_min = None, s_max = None, best = None)
    
    toolbox = base.Toolbox()
    toolbox.register("particle", generate_particle, s_min = -max_s, s_max = max_s)
    toolbox.register("population", tools.initRepeat, list, toolbox.particle)
    toolbox.register("update", update_particle, w = weight, phi1 = phi1, phi2 = phi2)
    toolbox.register("evaluate", get_fitness)
    
    popu = toolbox.population(n = pop_size)
    best = None
    iteration_no = 0
    prev_best = 10e5
    
    print("\nPSO is Starting...")
    # start = time.time()
    
    for gen in range(max_iterations):
        repeated = 0
        if gen % 100 == 0:
            print(f"Best till now : {best}")
        for part in popu:
            part.fitness.values = toolbox.evaluate(part)
            if part.fitness.values[0] < prev_best:
                prev_best = part.fitness.values[0]
                iteration_no = gen + 1
                print(iteration_no)
            elif part.fitness.values[0] == prev_best:
                repeated += 1
        
        if repeated > int(np.ceil(0.20*pop_size)):
            alternate_popu = toolbox.population(n = pop_size)
            for particle in alternate_popu:
                particle.fitness.values = toolbox.evaluate(particle)
            some = int(np.ceil(0.1*pop_size))
            some_popu = tools.selRandom(alternate_popu, some)
            temp_popu = tools.selWorst(popu, pop_size - some)
        else:
            some = int(np.ceil(0.05*pop_size))
            some_popu = tools.selBest(popu, some)
            temp_popu = tools.selRandom(popu, pop_size - some)
        
        temp_popu = list(map(toolbox.clone, temp_popu))
        
        for particle in temp_popu:
            if not particle.best or particle.fitness < particle.best.fitness:
                particle.best = creator.Particle(particle)
                particle.best.fitness.values = particle.fitness.values
            if not best or particle.fitness < best.fitness:
                print(f"Actual - {particle}")
                best = creator.Particle(particle)
                print(f"Function - {best}")
                best.fitness.values = particle.fitness.values
        # print(best)
        for particle in temp_popu:
            toolbox.update(particle, best)

        temp_popu.extend(some_popu)
        popu[:] = temp_popu
    
    # end = time.time()
    print("\nPSO Ends...")
    best_particle = tools.selBest(popu, 1)[0]
    # best_particle = best
    print(f"\nBest Particle or Best Path : {best_particle}")
    best_solution = get_fitness(best_particle)[0]
    best_found = iteration_no
    print(f"\nBest Solution = {best_solution}")
    print(f"\nBest solution found in {best_found}-iterations.")
    # print("\nTotal time taken = {round(end - start, 3)} sec.")
    
    return best_particle, best_solution


run_pso()
        














