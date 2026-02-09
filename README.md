# PageRank Assignment

This repository contains an implementation of the PageRank algorithm using a
graph representation along with supporting statistics and unit tests.

## Project Structure
```text
pagerank-assignment/
├── pagerank_gcs/     # PageRank implementation (graph, stats, algorithm)
├── tests/            # Pytest unit tests
└── requirements.txt # Python dependencies



## Setup Instructions

Follow the steps below to set up and run the project.

### 1. Clone the repository
Clone the repository from GitHub and move into the project directory:
```bash
git clone https://github.com/2003Ankita/pagerank-assignment.git
cd pagerank-assignment

### Install dependencies
Install the required Python packages listed in requirements.txt:
pip install -r requirements.txt

### Run tests
Run all unit tests using pytest:
pytest
This will execute the tests in the tests/ directory and verify the correctness
of the PageRank implementation.

### Run PageRank
To execute the PageRank algorithm, run the following command from the project root:
python -m pagerank_gcs.main
This command runs the main.py module inside the pagerank_gcs package.
