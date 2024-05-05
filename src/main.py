import time
import geopandas as gpd
from gerrychain import (
    Graph,
    Partition,
    proposals,
    updaters,
    constraints,
    accept,
    MarkovChain,
    Election,
)
from functools import partial
import matplotlib.pyplot as plt
from gerrychain.metrics import mean_median, efficiency_gap
from tqdm import tqdm
import numpy as np
import pandas as pd
from utils import bcolors

NUM_STEPS = 20_000

# Load the data
print(f"{bcolors.OKCYAN}🚚 Loading the data...{bcolors.ENDC}")
start_time = time.time()
ohio = gpd.read_file("../data/Ohio.shp")

oh_graph = Graph.from_geodataframe(ohio)


num_districts = 15
total_population = sum([oh_graph.nodes()[v]["TOTPOP"] for v in oh_graph.nodes()])
ideal_population = total_population / num_districts
population_tolerance = 0.02


cutedge_ensemble = []

districts_won_by_democrat_in_pres16 = []
districts_won_by_democrat_in_sen16 = []

mean_median_pres = []
mean_median_sen = []
efficiency_gap_pres = []
efficiency_gap_sen = []

wins_by_district_pres16 = []
wins_by_district_sen16 = []

# Create an initial partition
print(f"{bcolors.OKCYAN}🏗️  Creating an initial partition...{bcolors.ENDC}")
initial_partition = Partition(
    oh_graph,
    assignment="CONG_DIST",
    updaters={
        "populaton": updaters.Tally("TOTPOP", alias="populaton"),
        "cut_edges": updaters.cut_edges,
        "dem_won_pres": Election(
            "2016 presidential",
            {"Dem": "PRES16D", "Rep": "PRES16R"},
            alias="dem_won_pres",
        ),
        "dem_won_sen": Election(
            "2016 senatorial",
            {"Dem": "USS16D", "Rep": "USS16R"},
            alias="dem_won_sen",
        ),
    },
)

# Create an initial proposal
print(f"{bcolors.OKCYAN}📜 Creating an initial proposal...{bcolors.ENDC}")
proposal = partial(
    proposals.recom,
    pop_col="TOTPOP",
    pop_target=ideal_population,
    epsilon=population_tolerance,
    node_repeats=2,
)

# Create a constraint
print(f"{bcolors.OKCYAN}🔒 Creating a population constraint...{bcolors.ENDC}")
population_constraint = constraints.within_percent_of_ideal_population(
    initial_partition, population_tolerance, pop_key="populaton"
)

# Create a Markov chain
print(f"{bcolors.OKCYAN}🔗 Creating a Markov chain...{bcolors.ENDC}")
chain = MarkovChain(
    proposal=proposal,
    constraints=[
        population_constraint,
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=NUM_STEPS,
)

print(f"{bcolors.WARNING}\n🚨 Running the chain...{bcolors.ENDC}")

for partition in tqdm(chain):
    cutedge_ensemble.append(len(partition["cut_edges"]))

    districts_won_by_democrat_in_pres16.append(partition["dem_won_pres"].wins("Dem"))
    districts_won_by_democrat_in_sen16.append(partition["dem_won_sen"].wins("Dem"))

    mean_median_pres.append(mean_median(partition["dem_won_pres"]))
    mean_median_sen.append(mean_median(partition["dem_won_sen"]))
    efficiency_gap_pres.append(efficiency_gap(partition["dem_won_pres"]))
    efficiency_gap_sen.append(efficiency_gap(partition["dem_won_sen"]))

    wins_by_district_pres16.append(sorted(partition["dem_won_pres"].percents("Dem")))
    wins_by_district_sen16.append(sorted(partition["dem_won_sen"].percents("Dem")))


## draw histogram of the above ensemble
print(f"\n{bcolors.OKPINK}🎨 Drawing graph for cut edges{bcolors.ENDC}")
plt.figure()
plt.hist(cutedge_ensemble, align="left")
plt.axvline(len(initial_partition["cut_edges"]), color="red", linestyle="--")
plt.legend(["Initial partition value"])
plt.xlabel("Number of cut edges")
plt.ylabel("Frequency")
plt.title("Number of cut edges by plans")
plt.savefig("../output/cut_edges.png")

print(f"{bcolors.OKPINK}🎨 Drawing graph for Dem presidential wins{bcolors.ENDC}")
plt.figure()
labels, counts = np.unique(districts_won_by_democrat_in_pres16, return_counts=True)
plt.bar(labels, counts, align="center")
plt.gca().set_xticks(labels)
plt.axvline(initial_partition["dem_won_pres"].wins("Dem"), color="red", linestyle="--")
plt.legend(["Initial partition value"])
plt.xlabel("Number of districts")
plt.ylabel("Steps")
plt.title("Districts won by Democrats in 2016 presidential election")
plt.savefig("../output/dem_pres16.png")

print(f"{bcolors.OKPINK}🎨 Drawing graph for Rep presidential wins{bcolors.ENDC}")
plt.figure()
labels, counts = np.unique(districts_won_by_democrat_in_sen16, return_counts=True)
plt.bar(labels, counts, align="center")
plt.gca().set_xticks(labels)
plt.axvline(initial_partition["dem_won_sen"].wins("Dem"), color="red", linestyle="--")
plt.legend(["Initial partition value"])
plt.xlabel("Number of districts")
plt.ylabel("Steps")
plt.title("Districts won by Democrats in 2016 senatorial election")
plt.savefig("../output/dem_sen16.png")


# -------------------------------------------------------
# Mean Median and Efficiency Gap analysis
# -------------------------------------------------------

print(
    f"{bcolors.OKPINK}📊 Generating mean-median analysis for pres election{bcolors.ENDC}"
)
plt.figure()
plt.hist(mean_median_pres)
plt.axvline(mean_median(initial_partition["dem_won_pres"]), color="red", linestyle="--")
plt.legend(["Initial partition value"])
plt.xlabel("Mean-median difference")
plt.ylabel("Steps")
plt.title("Mean-median difference for Dem presidential election in 2016")
plt.savefig("../output/mean_median_pres16.png")

print(
    f"{bcolors.OKPINK}📊 Generating mean-median analysis for sen election{bcolors.ENDC}"
)
plt.figure()
plt.hist(mean_median_sen)
plt.axvline(mean_median(initial_partition["dem_won_sen"]), color="red", linestyle="--")
plt.legend(["Initial partition value"])
plt.xlabel("Mean-median difference")
plt.ylabel("Steps")
plt.title("Mean-median difference for Dem senatorial election in 2016")
plt.savefig("../output/mean_median_sen16.png")


print(
    f"{bcolors.OKPINK}📊 Generating efficiency gap analysis for pres election{bcolors.ENDC}"
)
plt.figure()
plt.hist(efficiency_gap_pres)
plt.axvline(
    efficiency_gap(initial_partition["dem_won_pres"]), color="red", linestyle="--"
)
plt.legend(["Initial partition value"])
plt.xlabel("Efficiency gap")
plt.ylabel("Steps")
plt.title("Efficiency gap for Dem presidential election in 2016")
plt.savefig("../output/efficiency_gap_pres16.png")

print(
    f"{bcolors.OKPINK}📊 Generating efficiency gap analysis for sen election{bcolors.ENDC}"
)
plt.figure()
plt.hist(efficiency_gap_sen)
plt.axvline(
    efficiency_gap(initial_partition["dem_won_sen"]), color="red", linestyle="--"
)
plt.legend(["Initial partition value"])
plt.xlabel("Efficiency gap")
plt.ylabel("Steps")
plt.title("Efficiency gap for Dem senatorial election in 2016")
plt.savefig("../output/efficiency_gap_sen16.png")


# -------------------------------------------------------
# Marginal box plots analysis
# -------------------------------------------------------


print(
    f"\n{bcolors.OKPINK}🕯️  Generating marginal box plots for Dem presidential election{bcolors.ENDC}"
)

data = pd.DataFrame(wins_by_district_pres16)

fig, ax = plt.subplots(figsize=(8, 6))
ax.axhline(0.5, color="#ff0000", linestyle="--")
data.boxplot(ax=ax, positions=range(len(data.columns)))
plt.plot(data.iloc[0], "ro")

# Annotate
ax.set_title("Marginal box plot for Democrats presidential wins in 2016")
ax.set_ylabel("Democratic vote % (President 2016)")
ax.set_xlabel("Sorted districts")
ax.set_ylim(0, 1)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
fig.savefig("../output/marginal_pres16.png")


print(
    f"\n{bcolors.OKPINK}🕯️  Generating marginal box plots for Dem senatorial election{bcolors.ENDC}"
)

data = pd.DataFrame(wins_by_district_sen16)

fig, ax = plt.subplots(figsize=(8, 6))
ax.axhline(0.5, color="#ff0000", linestyle="--")
data.boxplot(ax=ax, positions=range(len(data.columns)))
plt.plot(data.iloc[0], "ro")

# Annotate
ax.set_title("Marginal box plot for Democrats senatorial wins in 2016")
ax.set_ylabel("Democratic vote % (Senate 2016)")
ax.set_xlabel("Sorted districts")
ax.set_ylim(0, 1)
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
fig.savefig("../output/marginal_sen16.png")


end_time = time.time()
print(
    f"\n{bcolors.OKGREEN}✅ The time to run the whole analysis is {end_time - start_time} seconds{bcolors.ENDC}"
)
