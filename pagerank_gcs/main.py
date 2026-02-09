import argparse
import time
from pagerank_gcs.gcs_graph import read_graph_from_gcs
from pagerank_gcs.stats import degree_stats
from pagerank_gcs.pagerank import pagerank_iterative

def top_k(pr_dict, k=5):
    return sorted(pr_dict.items(), key=lambda x: x[1], reverse=True)[:k]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True, help="GCS bucket name (e.g., pagerank-bu-ap178152)")
    parser.add_argument("--prefix", required=True, help="Prefix under bucket (e.g., webgraph/)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of HTML files to process (faster runs)")
    parser.add_argument("--damping", type=float, default=0.85)
    parser.add_argument("--tol", type=float, default=0.005, help="0.005 = 0.5% convergence threshold")
    parser.add_argument("--max-iter", type=int, default=200)
    args = parser.parse_args()

    t0 = time.time()
    outlinks, out_deg, in_deg = read_graph_from_gcs(args.bucket, args.prefix, limit=args.limit)
    t1 = time.time()

    out_stats = degree_stats(out_deg)
    in_stats = degree_stats(in_deg)

    pr, iters = pagerank_iterative(outlinks, damping=args.damping, tol_ratio=args.tol, max_iter=args.max_iter)
    t2 = time.time()

    print("=== Outgoing Links Stats ===")
    print(out_stats)
    print("\n=== Incoming Links Stats ===")
    print(in_stats)

    print(f"\n=== PageRank (iterations={iters}) Top 5 ===")
    for pid, score in top_k(pr, 5):
        print(f"{pid}\t{score:.10f}")

    print("\n=== Timing ===")
    print(f"Read/build graph: {t1 - t0:.2f}s")
    print(f"PageRank compute: {t2 - t1:.2f}s")
    print(f"Total:           {t2 - t0:.2f}s")

if __name__ == "__main__":
    main()
