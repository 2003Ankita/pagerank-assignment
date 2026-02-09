from pagerank_gcs.pagerank import pagerank_iterative

def test_pagerank_fixed_graph_top_node():
    # Fixed graph with 4 nodes:
    # 0 -> 1,2
    # 1 -> 2
    # 2 -> 0
    # 3 -> (dangling)
    outlinks = {
        0: [1, 2],
        1: [2],
        2: [0],
        3: []
    }

    pr, iters = pagerank_iterative(outlinks, damping=0.85, tol_ratio=0.005, max_iter=500)

    # Basic invariants
    assert iters >= 1
    assert abs(sum(pr.values()) - 1.0) < 1e-9
    for v in pr.values():
        assert v >= 0.0

    # Expected: node 2 is top (it receives links from 0 and 1)
    top_node = max(pr.items(), key=lambda x: x[1])[0]
    assert top_node == 2

    # Loose sanity ranges (catches major bugs but doesn't overfit)
    assert 0.20 <= pr[2] <= 0.50
    assert 0.03 <= pr[3] <= 0.35

