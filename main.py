# import maup
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

NUM_STEPS = 20_000


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKPINK = "\u001b[38;5;201m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Load the data
print(f"{bcolors.OKCYAN}🚚 Loading the data...{bcolors.ENDC}")
start_time = time.time()
ohio = gpd.read_file("Ohio.shp")

oh_graph = Graph.from_geodataframe(ohio)


num_districts = 15
total_population = sum([oh_graph.nodes()[v]["TOTPOP"] for v in oh_graph.nodes()])
ideal_population = total_population / num_districts
population_tolerance = 0.02


cutedge_ensemble = []
population_ensemble = []

districts_won_by_democrat_in_pres16 = []
districts_won_by_democrat_in_sen16 = []

maj_white_ensemble = []
maj_black_ensemble = []

mean_median_pres = []
mean_median_sen = []
efficiency_gap_pres = []
efficiency_gap_sen = []

wins_by_district_pres16 = [[] for _ in range(num_districts)]
wins_by_district_sen16 = [[] for _ in range(num_districts)]

# Create an initial partition
print(f"{bcolors.OKCYAN}🏗️  Creating an initial partition...{bcolors.ENDC}")
initial_partition = Partition(
    oh_graph,
    assignment="CONG_DIST",
    updaters={
        "populaton": updaters.Tally("TOTPOP", alias="populaton"),
        "cut_edges": updaters.cut_edges,
        "white": updaters.Tally("NH_WHITE", alias="white"),
        "black": updaters.Tally("NH_BLACK", alias="black"),
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
    population_ensemble.append(sorted(partition["populaton"].values()))

    districts_won_by_democrat_in_pres16.append(partition["dem_won_pres"].wins("Dem"))
    districts_won_by_democrat_in_sen16.append(partition["dem_won_sen"].wins("Dem"))

    mean_median_pres.append(mean_median(partition["dem_won_pres"]))
    mean_median_sen.append(mean_median(partition["dem_won_sen"]))
    efficiency_gap_pres.append(efficiency_gap(partition["dem_won_pres"]))
    efficiency_gap_sen.append(efficiency_gap(partition["dem_won_sen"]))

    num_white = 0
    num_black = 0

    for i in range(1, num_districts + 1):
        w_prec = partition["white"][i]
        b_prec = partition["black"][i]

        # find the max population and increment the corresponding counter
        max_prec = max(w_prec, b_prec)
        if max_prec == w_prec:
            num_white += 1
        elif max_prec == b_prec:
            num_black += 1
        wins_by_district_pres16[i - 1].append(
            partition["dem_won_pres"].percent("Dem", i)
        )
        wins_by_district_sen16[i - 1].append(partition["dem_won_sen"].percent("Dem", i))

    maj_black_ensemble.append(num_black)
    maj_white_ensemble.append(num_white)


## draw histogram of the above ensemble
print(f"\n{bcolors.OKPINK}🎨 Drawing graph for cut edges{bcolors.ENDC}")
plt.figure()
plt.hist(cutedge_ensemble, align="left")
plt.xlabel("Number of cut edges")
plt.ylabel("Frequency")
plt.title("Histogram of the number of cut edges")
plt.savefig("cut_edges.png")

print(f"{bcolors.OKPINK}🎨 Drawing graph for population{bcolors.ENDC}")
plt.figure()
plt.hist(population_ensemble, align="left")
plt.xlabel("Population")
plt.ylabel("Frequency")
plt.title("Histogram of the population")
plt.savefig("population.png")

print(f"{bcolors.OKPINK}🎨 Drawing graph for Dem presidential wins{bcolors.ENDC}")
plt.figure()
plt.hist(districts_won_by_democrat_in_pres16, align="left")
plt.xlabel("Number of districts won by Democrats in 2016 presidential")
plt.ylabel("Steps")
plt.title("Histogram of the number of districts won by Democrats in 2016 presidential")
plt.savefig("dem_pres16.png")

print(f"{bcolors.OKPINK}🎨 Drawing graph for Rep presidential wins{bcolors.ENDC}")
plt.figure()
plt.hist(districts_won_by_democrat_in_sen16, align="left")
plt.xlabel("Number of districts won by Democrats in 2016 senatorial")
plt.ylabel("Steps")
plt.title("Histogram of the number of districts won by Democrats in 2016 senatorial")
plt.savefig("dem_sen16.png")

print(f"{bcolors.OKPINK}🎨 Drawing graph for majority White VAP{bcolors.ENDC}")
plt.figure()
plt.hist(maj_white_ensemble, align="left")
plt.xlabel("Number of majority White VAP districts")
plt.ylabel("Steps")
plt.title("Histogram of the number of majority White VAP districts")
plt.savefig("maj_white.png")

print(f"{bcolors.OKPINK}🎨 Drawing graph for majority Black VAP{bcolors.ENDC}")
plt.figure()
plt.hist(maj_black_ensemble, align="left")
plt.xlabel("Number of majority Black VAP districts")
plt.ylabel("Steps")
plt.title("Histogram of the number of majority Black VAP districts")
plt.savefig("maj_black.png")

# -------------------------------------------------------
# Mean Median and Efficiency Gap analysis
# -------------------------------------------------------

print(
    f"\n{bcolors.OKPINK}📊 Generating mean-median analysis for pres and sen elections{bcolors.ENDC}"
)
plt.figure()
plt.plot(mean_median_pres, label="Presidential")
plt.plot(mean_median_sen, label="Senatorial")
# mark the 0 line
plt.axhline(0, color="black", linestyle="--")
plt.title("Mean-median difference for presidential and senatorial elections")
plt.xlabel("Steps")
plt.ylabel("Mean-median difference")
plt.legend()
plt.savefig("mean_median.png")

print(
    f"{bcolors.OKPINK}📊 Generating efficiency gap analysis for pres and sen elections{bcolors.ENDC}"
)
plt.figure()
plt.plot(efficiency_gap_pres, label="Presidential")
plt.plot(efficiency_gap_sen, label="Senatorial")
# mark the 0 line
plt.axhline(0, color="black", linestyle="--")
plt.title("Efficiency gap for presidential and senatorial elections")
plt.xlabel("Steps")
plt.ylabel("Efficiency gap")
plt.legend()
plt.savefig("efficiency_gap.png")


# -------------------------------------------------------
# Marginal box plots analysis
# -------------------------------------------------------

# Marginal box plots for dem won pres16 for each district, x axis is the number of
# districts and y axis is the % of wins. each district comes from the
# partition in chain.

print(
    f"\n{bcolors.OKPINK}🕯️  Generating marginal box plots for Dem presidential election{bcolors.ENDC}"
)

plt.figure()
plt.boxplot(wins_by_district_pres16)
plt.xlabel("Districts")
plt.ylabel("% of wins")
# mark the 50% line
plt.axhline(0.5, color="black", linestyle="--")
plt.title("Marginal box plot for Democrats presidential wins in 2016")
plt.savefig("marginal_pres16.png")


# Marginal box plots for dem won sen16
print(
    f"{bcolors.OKPINK}🕯️  Generating marginal box plots for Dem senatorial election{bcolors.ENDC}"
)
plt.figure()
plt.boxplot(wins_by_district_sen16)
plt.xlabel("Districts")
plt.ylabel("% of wins")
# mark the 50% line
plt.axhline(0.5, color="black", linestyle="--")
plt.title("Marginal box plot for Democrats senatorial wins in 2016")
plt.savefig("marginal_sen16.png")

end_time = time.time()
print(
    f"\n{bcolors.OKGREEN}✅ The time to run the whole analysis is {end_time - start_time} seconds{bcolors.ENDC}"
)
