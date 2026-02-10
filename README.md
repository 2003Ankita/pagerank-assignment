# PageRank Assignment
This repository contains an implementation of the PageRank algorithm using a
graph representation along with supporting statistics and unit tests.

## Project Structure
```text
pagerank-assignment/
├── pagerank_gcs/     # PageRank implementation (graph, stats, algorithm)
├── tests/            # Pytest unit tests
└── requirements.txt # Python dependencies

## Project Details

- **GCP Project ID**: sustained-flow-485619-g3
- **GCS Bucket**: pagerank-bu-ap178152
- **Region**: us-central1
- **Data prefix**: webgraph_v2/

## Setup Instructions

Follow the steps below to set up and run the project.

### 1. Clone the repository
Clone the repository from GitHub and move into the project directory:
```bash
git clone https://github.com/2003Ankita/pagerank-assignment.git
cd pagerank-assignment

### Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

### Install dependencies
Install the required Python packages listed in requirements.txt:
pip install -r requirements.txt

### Run tests
Run all unit tests using pytest:
pytest
This runs the tests in the tests/ directory and verifies correctness on a
small deterministic graph (independent of the randomly generated 20K files).

## Run PageRank on GCS data
To execute the PageRank algorithm, run the following command from the project root:
```bash
PYTHONPATH=. python -m pagerank_gcs.main \
--bucket pagerank-bu-ap178152 \
--prefix webgraph_v2/ \
--limit 20000 | tee cloudshell_output_20k.txt


Parameter meanings
--bucket : Name of the GCS bucket containing the HTML files
--prefix : Directory inside the bucket where HTML files are stored
--limit : Maximum number of HTML files to process (optional, speeds up testing)

The bucket was made world-readable so TAs can access the data:
```bash
gsutil iam ch allUsers:objectViewer gs://pagerank-bu-ap178152

We implemented the original iterative PageRank algorithm:
PR(A) = 0.15 / N + 0.85 * Σ (PR(T) / C(T))
- Iteration stops when total PageRank changes by less than **0.5%**
- Dangling nodes (pages with zero outgoing links) are handled by redistributing their rank uniformly
