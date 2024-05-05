#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Citational Information:
This code is based on the code:  https://github.com/vrdi/shortbursts-gingles/blob/main/state_experiments/sb_runs.py

Multi-processing:
To speed up the process, we use the multiprocessing library to run the short bursts in parallel.
The number of processes is defined by the MAX_PROCESSES variable.

Minority Population:
The minority population is defined by the MIN_POP_COL variable. In this case, we are using the Black Voting Age Population (BVAP).
This is because in Ohio, the BVAP is the minority population that has the most significant impact on the electoral results, especially in district 11
where the BVAP is slightly more than the White Voting Age Population (WVAP).
"""
import geopandas as gpd
import numpy as np
import pickle
from gerrychain import Graph, Partition
from gerrychain.updaters import Tally
from gingleator import Gingleator
import multiprocessing

from utils import bcolors



# initial setups
STATE = "OH"
NUM_DISTRICTS = 15
POP_COL = "TOTPOP"
MIN_POP_COL = "BVAP"
POP_TOT = 0.02

BURST_LENS = [5, 10, 15] 
SCORE_FUNCT = Gingleator.num_opportunity_dists 
THRESHOLDS = [0.4, 0.45, 0.5] 
ITERS = 20000

# to run in parallel
MAX_PROCESSES = 20 

print(f"{bcolors.OKCYAN}🚚 Loading the data...{bcolors.ENDC}")
ohio = gpd.read_file("../data/Ohio.shp")
graph = Graph.from_geodataframe(ohio)


my_updaters = {"population" : Tally(POP_COL, alias="population"),
               "VAP": Tally("VAP"),
               "BVAP": Tally("BVAP")}


print(f"{bcolors.OKCYAN}🏗️  Creating an initial partition...{bcolors.ENDC}")
initial_partition = Partition(
    graph=graph,
    assignment="CONG_DIST",
    updaters=my_updaters
)


def sb_worker(threshold, burst_len):
    """
    A worker function that runs the short bursts for a given threshold and burst length.
    Intended to be used in a multiprocessing pool.

    Parameters:
    threshold (float): The threshold for the short bursts.
    burst_len (int): The length of each burst.
    """
    params = f"{STATE}_dists{NUM_DISTRICTS}_{MIN_POP_COL}opt_{POP_TOT:.1%}_{ITERS}_sbl{burst_len}_score{SCORE_FUNCT.__name__}_{threshold}"

    
    num_bursts = ITERS//burst_len
    
    gingles = Gingleator(initial_partition, pop_col=POP_COL,
                         threshold=threshold, score_funct=SCORE_FUNCT, epsilon=POP_TOT,
                         minority_perc_col="{}_perc".format(MIN_POP_COL))

    
    gingles.init_minority_perc_col(MIN_POP_COL, "VAP", "{}_perc".format(MIN_POP_COL))

    print(f"{bcolors.WARNING} Running short bursts for threshold = {threshold} and burst_len= {burst_len}{bcolors.ENDC}", flush=True)

    sb_obs = gingles.short_burst_run(num_bursts=num_bursts, num_steps=burst_len,
                                     maximize=True, verbose=True)

    print(f"{bcolors.OKGREEN}🎉 Short bursts completed!{bcolors.ENDC}", flush=True)

    print(f"{bcolors.OKCYAN}📊 Saving the results...{bcolors.ENDC}")

    f_out_res = f"../data/{params}.npy"
    np.save(f_out_res, sb_obs[1])

    f_out_stats = f"../data/{params}.p"
    max_stats = {"VAP": sb_obs[0][0]["VAP"],
                 "BVAP": sb_obs[0][0]["BVAP"]}

    with open(f_out_stats, "wb") as f_out:
        pickle.dump(max_stats, f_out)

if __name__ == '__main__':
    with multiprocessing.Pool(processes=MAX_PROCESSES) as pool:
        pool.starmap(sb_worker, [(th, bl) for th in THRESHOLDS for bl in BURST_LENS])