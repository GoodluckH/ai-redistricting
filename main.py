# import maup
import time
import geopandas as gpd
import pandas as pd
from gerrychain import Graph, Partition, proposals, updaters, constraints, accept, MarkovChain, Election
from functools import partial


# maup.progress.enabled = True



# Load the data
start_time = time.time()
ohio = gpd.read_file("Ohio.shp")

oh_graph = Graph.from_geodataframe(ohio)


## print all the columns
print(ohio.columns)

num_districts = 15
total_population = sum([oh_graph.nodes()[v]["TOTPOP"] for v in oh_graph.nodes()])
ideal_population = total_population / num_districts
population_tolerance = 0.02

# TODO: delete all races other than white and black
# TODO: add dem/rep votes for pres16 and sen16
# TODO: see lab 2
# TODO: efficiency gap analysis - each party in each district, twin bar graphs to show the wasted votes
# TODO: mean median analysis 

# TODO: short burst and marginal box plots
cutedge_ensemble = []
population_ensemble = []
districts_won_by_republican_in_pres16 = []
districts_won_by_republican_in_sen16 = []
districts_won_by_democrat_in_pres16 = []
districts_won_by_democrat_in_sen16 = []
maj_hisp_ensemble = []
maj_white_ensemble = []
maj_black_ensemble = []
maj_asian_ensemble = []
maj_native_ensemble = []

# Create an initial partition
initial_partition = Partition(
    oh_graph,
    assignment="CONG_DIST",
    updaters={
        "populaton": updaters.Tally("TOTPOP", alias="populaton"),
        "cut_edges": updaters.cut_edges,
        "hisp": updaters.Tally("HISP", alias="hisp"),
        "white": updaters.Tally("NH_WHITE", alias="white"),
        "black": updaters.Tally("NH_BLACK", alias="black"),
        "asian": updaters.Tally("NH_ASIAN", alias="asian"),
        "native": updaters.Tally("NH_AMIN", alias="native"),
    }
)

# Create an initial proposal
proposal = partial(
    proposals.recom,
    pop_col="TOTPOP",
    pop_target=ideal_population,
    epsilon=population_tolerance,
    node_repeats=2,
)

# Create a constraint
population_constraint = constraints.within_percent_of_ideal_population(initial_partition, population_tolerance, pop_key="populaton")

# Create a Markov chain
chain = MarkovChain(
    proposal=proposal,
    constraints=[
        population_constraint,
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=3000,
)

print("Start running the chain")

# Run the chain
for partition in chain:
    cutedge_ensemble.append(len(partition["cut_edges"]))
    population_ensemble.append(sorted(partition["populaton"].values()))
    
    num_white = 0
    num_hisp = 0
    num_black = 0
    num_asian = 0
    num_native = 0

    for i in range(1, num_districts + 1):
        w_prec = partition["white"][i]
        h_prec = partition["hisp"][i]
        b_prec = partition["black"][i]
        a_prec = partition["asian"][i]
        n_prec = partition["native"][i]

        # find the max population and increment the corresponding counter
        max_prec = max(w_prec, h_prec, b_prec, a_prec, n_prec)
        if max_prec == w_prec:
            num_white += 1
        elif max_prec == h_prec:
            num_hisp += 1
        elif max_prec == b_prec:
            num_black += 1
        elif max_prec == a_prec:
            num_asian += 1
        elif max_prec == n_prec:
            num_native += 1

    maj_hisp_ensemble.append(num_hisp)
    maj_black_ensemble.append(num_black)
    maj_asian_ensemble.append(num_asian)
    maj_native_ensemble.append(num_native)
    maj_white_ensemble.append(num_white)




## draw histogram of the above ensemble
import matplotlib.pyplot as plt
import numpy as np

plt.figure()
plt.hist(cutedge_ensemble, align="left")
plt.xlabel("Number of cut edges")
plt.ylabel("Frequency")
plt.title("Histogram of the number of cut edges")
plt.savefig("cut_edges.png")

plt.figure()
plt.hist(population_ensemble, align="left")
plt.xlabel("Population")
plt.ylabel("Frequency")
plt.title("Histogram of the population")
plt.savefig("population.png")

plt.figure()
plt.hist(maj_white_ensemble, align="left")
plt.xlabel("Number of majority White VAP districts")
plt.ylabel("Frequency")
plt.title("Histogram of the number of majority White VAP districts")
plt.savefig("maj_white.png")

plt.figure()
plt.hist(maj_hisp_ensemble, align="left")
plt.xlabel("Number of majority Hispanic VAP districts")
plt.ylabel("Frequency")
plt.title("Histogram of the number of majority Hispanic VAP districts")
plt.savefig("maj_hisp.png")

plt.figure()
plt.hist(maj_black_ensemble, align="left")
plt.xlabel("Number of majority Black VAP districts")
plt.ylabel("Frequency")
plt.title("Histogram of the number of majority Black VAP districts")
plt.savefig("maj_black.png")

plt.figure()
plt.hist(maj_asian_ensemble, align="left")
plt.xlabel("Number of majority Asian VAP districts")
plt.ylabel("Frequency")
plt.title("Histogram of the number of majority Asian VAP districts")
plt.savefig("maj_asian.png")


plt.figure()
plt.hist(maj_native_ensemble, align="left")
plt.xlabel("Number of majority Native VAP districts")
plt.ylabel("Frequency")
plt.title("Histogram of the number of majority Native VAP districts")
plt.savefig("maj_native.png")


end_time = time.time()
print("The time to import il_pl2020_p2_b.shp is:", (end_time - start_time) / 60, "mins")
