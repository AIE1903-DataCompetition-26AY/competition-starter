# AIE1903 group project

Replace this title with your group name. Record all members and GitHub usernames here.

## Access

Use one **private repository per group**. Give course staff access and give only your group members write access. This folder is a starter, not an already-created GitHub repository. Use the instructor's verified course data repository to download the data separately.

## Setup

Use Python 3.11 or newer. From the repository root:

```bash
python -m venv .venv
# Activate .venv using your operating system's command, then:
python -m pip install -r requirements.txt
python -m jupyterlab notebooks/01_eda.ipynb
```

Place authorized copies of `train.csv` and `test.csv` in `data/`. The CSVs and `.env` are ignored by Git. **An ignore rule does not remove a file already tracked in history.** Inspect `git diff --cached` before every commit; never commit secrets, hidden test ground truth, or restricted raw data.

For a command-line run:

```bash
python src/competition_eda.py --data-dir data --cell Cell_177 --output-dir reports
```

The script validates the file contract and creates a chronological time plot and a complete-day seasonal overlay. It does not use or fabricate any test labels. The notebook also creates `reports/first_plot.png` for the lecture's Git demo.

## What to document

State your cell, data version, method, run command, software versions, and three observations. Distinguish observations from hypotheses. Keep units as anonymized raw counts; do not assign a time zone or geographic location that the description does not provide.

The starter deliberately contains no forecasting score, competition answer, or precomputed traffic chart.

## Collaboration

Work on a branch, commit a small coherent change, push, and open a pull request to `main`. Ask another group member to review before merging. Clear notebook outputs that could expose restricted information. Record each member's contribution.

If an API or AI coding tool is used, follow the instructor's data-use and spending policy. Never put an access key in a notebook, source file, commit, or screenshot.
