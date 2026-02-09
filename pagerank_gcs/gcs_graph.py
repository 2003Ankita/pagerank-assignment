import re
import requests
import subprocess
from typing import Dict, List, Tuple

HREF_RE = re.compile(r'HREF="(\d+)\.html"', re.IGNORECASE)


def parse_outgoing_links(html_bytes: bytes) -> List[int]:
    text = html_bytes.decode("utf-8", errors="ignore")
    return [int(m.group(1)) for m in HREF_RE.finditer(text)]


def list_html_objects_public(bucket: str, prefix: str, limit: int | None = None) -> List[str]:
    """
    Lists objects using gsutil (works for public buckets without Python credentials).
    Returns object names like: webgraph/123.html

    limit: if set, only return up to 'limit' objects (useful to make Cloud Shell fast).
    """
    cmd = ["gsutil", "ls", f"gs://{bucket}/{prefix}*.html"]
    out = subprocess.check_output(cmd, text=True)

    names = [line.strip().replace(f"gs://{bucket}/", "") for line in out.splitlines()]
    if limit is not None:
        names = names[:limit]
    return names


def download_object_public(bucket: str, object_name: str) -> bytes:
    """
    Downloads a single object via public HTTPS endpoint (no auth).
    """
    url = f"https://storage.googleapis.com/{bucket}/{object_name}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content


def read_graph_from_gcs(
    bucket: str,
    prefix: str,
    limit: int | None = None
) -> Tuple[Dict[int, List[int]], Dict[int, int], Dict[int, int]]:

    object_names = list_html_objects_public(bucket, prefix, limit=limit)
    if not object_names:
        raise RuntimeError("No HTML files found under the given prefix")

    def page_id(name: str) -> int:
        return int(name.split("/")[-1].replace(".html", ""))

    page_ids = [page_id(n) for n in object_names]
    n = max(page_ids) + 1

    outlinks: Dict[int, List[int]] = {i: [] for i in range(n)}
    in_degree: Dict[int, int] = {i: 0 for i in range(n)}

    for name in object_names:
        pid = page_id(name)
        content = download_object_public(bucket, name)
        outlinks[pid] = parse_outgoing_links(content)

    for src in range(n):
        for dst in outlinks[src]:
            if 0 <= dst < n:
                in_degree[dst] += 1

    out_degree = {i: len(outlinks[i]) for i in range(n)}
    return outlinks, out_degree, in_degree
