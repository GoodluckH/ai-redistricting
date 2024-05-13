<p align="center">
  <img width="400" src="https://raw.githubusercontent.com/GoodluckH/ai-redistricting/668ee05c483495fefd754643eb7f96d2914f1754/assets/logo.svg">
</p>

---

<p align="center">
  <i>Political geometry analysis of Ohio</i>
</p>

<p align="center">
  <a href="/LICENSE"><img alt="MIT" src="https://img.shields.io/github/license/goodluckh/ai-redistricting?style=flat-square"></a>
  <a href='http://makeapullrequest.com'><img alt='PRs Welcome' src='https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square'/></a>
  <a href="https://github.com/goodluckh/ai-redistricting/graphs/commit-activity"><img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/m/goodluckh/ai-redistricting?style=flat-square"/></a>
  <a href="https://github.com/goodluckh/ai-redistricting/issues"><img alt="GitHub closed issues" src="https://img.shields.io/github/issues-closed/goodluckh/ai-redistricting?style=flat-square"/></a>
</p>

## 👻 About

The Ohio redistricting project is a comprehensive analysis of the
political geometry of Ohio. The project aims to provide a detailed
analysis of the political landscape of Ohio, including the current
congressional districts, the demographic distribution, and the political
leanings of the state. The project will also explore the impact of
gerrymandering on the political landscape of Ohio and propose
alternative redistricting plans that are fair and representative of the
state's population.

## 📚 Guide

### 🗂️ Organization

The repository is organized as follows:

```bash
ai-redistricting/
├── assets/                 # Misc. assets
├── data/                   # Data files - shapefiles and short burst files
├── output/                 # Output images
├── src/                    # Source code
│   ├── main.py             # Main script for running the analysis
│   ├── Ohio_MAUP.ipynb     # Notebook used to produce shapefiles
│   ├── Ohio_SB.ipynb       # Notebook used to analyze short bursts
│   ├── sb.py               # Script for producing short bursts data
│   └── gingleator.py       # Gingleator helper for SB analysis
└──...
```

### 🚀 Quick Start

To reproduce the shapefiles, make sure you obtain the raw data from the
[Redistricting Data Hub](https://redistrictingdatahub.org/):

- [Census Data](https://redistrictingdatahub.org/dataset/ohio-block-pl-94171-2020-by-table/)
- [Congressional Districts](https://redistrictingdatahub.org/dataset/2022-ohio-congressional-districts-approved-plan/)
- [Election
  Data](https://redistrictingdatahub.org/dataset/vest-2016-ohio-precinct-and-election-results/)

Once you have them, change the import paths in the `Ohio_MAUP.ipynb`
file to point to the correct location of the data files.

### 📈 Analysis

Make sure you have the required libraries installed, then run the
following command:

```bash
cd src
python3 main.py
```

Output images will be saved in the `output/` directory.

To run the short burst analysis:

```bash
cd src
python3 sb.py
```

Output data files will be saved in the `data/` directory.

## 📝 License

This project is licensed under the MIT License - see the
[LICENSE](/LICENSE) file for details.
