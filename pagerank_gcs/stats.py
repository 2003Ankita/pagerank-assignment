from typing import Dict, Any
import numpy as np

def degree_stats(deg: Dict[int, int]) -> Dict[str, Any]:
    """
    Computes:
      Average, Median, Max, Min, Quintiles (20/40/60/80%)
    """
    arr = np.array(list(deg.values()), dtype=float)
    arr_sorted = np.sort(arr)

    quintiles = np.quantile(arr_sorted, [0.2, 0.4, 0.6, 0.8]).tolist()
    return {
        "average": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "quintiles_20_40_60_80": [float(x) for x in quintiles],
    }
