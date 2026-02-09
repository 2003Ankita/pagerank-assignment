from typing import Dict, List, Tuple

def pagerank_iterative(
    outlinks: Dict[int, List[int]],
    damping: float = 0.85,
    tol_ratio: float = 0.005,   # 0.5%
    max_iter: int = 200
) -> Tuple[Dict[int, float], int]:
    """
    Original iterative PageRank:
      PR(A) = (1-d)/n + d * sum_{T->A} PR(T)/C(T)

    Handles dangling nodes (C(T)=0) by distributing their rank uniformly.

    Convergence:
      stop when sum_i |PR_new(i) - PR_old(i)| <= tol_ratio * sum(PR_old)
    With normalization sum(PR_old)=1, this becomes <= 0.005.
    """
    n = len(outlinks)
    if n == 0:
        return {}, 0

    pr = {i: 1.0 / n for i in range(n)}
    base = (1.0 - damping) / n
    tol = tol_ratio * 1.0  # total rank mass ~ 1

    for it in range(1, max_iter + 1):
        new_pr = {i: base for i in range(n)}

        # Dangling rank mass
        dangling_mass = 0.0
        for i in range(n):
            if len(outlinks[i]) == 0:
                dangling_mass += pr[i]

        # Spread dangling mass uniformly
        if dangling_mass != 0.0:
            add = damping * dangling_mass / n
            for i in range(n):
                new_pr[i] += add

        # Spread rank from non-dangling nodes
        for src in range(n):
            outs = outlinks[src]
            c = len(outs)
            if c == 0:
                continue
            share = damping * pr[src] / c
            for dst in outs:
                if 0 <= dst < n:
                    new_pr[dst] += share

        # L1 change
        delta = sum(abs(new_pr[i] - pr[i]) for i in range(n))

        # Normalize for numerical stability
        s = sum(new_pr.values())
        if s != 0.0:
            for i in range(n):
                new_pr[i] /= s

        pr = new_pr
        if delta <= tol:
            return pr, it

    return pr, max_iter
