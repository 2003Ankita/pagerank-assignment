import re
import subprocess
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

HREF_RE = re.compile(r'HREF="(\d+)\.html"', re.IGNORECASE)

def parse_outgoing_links(html_bytes: bytes) -> List[int]:
    text = html_bytes.decode("utf-8", errors="ignore")
    return [int(m.group(1)) for m in HREF_RE.finditer(text)]

def list_html_objects_public(bucket: str, prefix: str, limit: Optional[int] = None) -> List[str]:
    cmd = ["gsutil", "ls", f"gs://{bucket}/{prefix}*.html"]
    out = subprocess.check_output(cmd, text=True)
    names = [line.strip().replace(f"gs://{bucket}/", "") for line in out.splitlines()]
    names.sort(key=lambda s: int(s.split("/")[-1].replace(".html", "")))  # stable order
    if limit:
        names = names[:limit]
    return names

def download_object_public(bucket: str, object_name: str) -> bytes:
    url = f"https://storage.googleapis.com/{bucket}/{object_name}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.content

def _fetch_and_parse(bucket: str, name: str) -> tuple[int, List[int]]:
    pid = int(name.split("/")[-1].replace(".html", ""))
    content = download_object_public(bucket, name)
    return pid, parse_outgoing_links(content)

def read_graph_from_gcs(
    bucket: str,
    prefix: str,
    limit: Optional[int] = None,
    workers: int = 64,
) -> Tuple[Dict[int, List[int]], Dict[int, int], Dict[int, int]]:

    object_names = list_html_objects_public(bucket, prefix, limit=limit)
    if not object_names:
        raise RuntimeError("No HTML files found")

    # N should be count of pages we are processing (limit-aware)
    page_ids = [int(n.split("/")[-1].replace(".html", "")) for n in object_names]
    n = max(page_ids) + 1   # assumes ids are 0..max; ok for your generator

    outlinks: Dict[int, List[int]] = {i: [] for i in range(n)}
    in_degree: Dict[int, int] = {i: 0 for i in range(n)}

    # ---- PARALLEL DOWNLOAD + PARSE ----
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [ex.submit(_fetch_and_parse, bucket, name) for name in object_names]
        for fut in as_completed(futures):
            pid, links = fut.result()
            outlinks[pid] = links

    # degrees
    for src in range(n):
        for dst in outlinks[src]:
            if 0 <= dst < n:
                in_degree[dst] += 1

    out_degree = {i: len(outlinks[i]) for i in range(n)}
    return outlinks, out_degree, in_degree
