# PageRank Assignment
## Project Structure
pagerank-assignment/
├── pagerank_gcs/ # PageRank implementation (graph, stats, algorithm)
├── tests/ # Pytest unit tests
├── requirements.txt # Python dependencies


## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/2003Ankita/pagerank-assignment.git
cd pagerank-assignment

### Install dependencies
pip install -r requirements.txt

### Run tests
pytest

### Run PageRank
python -m pagerank_gcs.main
