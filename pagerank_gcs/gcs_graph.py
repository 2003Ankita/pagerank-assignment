import re
import time
import requests
import subprocess
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


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

    connect_timeout = 10
    read_timeout = 120
    retries = 5

    last_exc = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=(connect_timeout, read_timeout))

            # Retry only for throttling / transient server errors
            if resp.status_code in (429, 500, 502, 503, 504):
                raise requests.exceptions.HTTPError(f"HTTP {resp.status_code}", response=resp)

            resp.raise_for_status()
            return resp.content

        except (requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError) as e:
            last_exc = e

        except requests.exceptions.HTTPError as e:
            last_exc = e
            # if it's NOT retryable, fail immediately
            code = getattr(e.response, "status_code", None)
            if code not in (429, 500, 502, 503, 504):
                raise

        time.sleep(2 ** attempt)

    raise last_exc


def _fetch_and_parse(bucket: str, name: str) -> tuple[int, List[int]]:
    pid = int(name.split("/")[-1].replace(".html", ""))
    content = download_object_public(bucket, name)
    return pid, parse_outgoing_links(content)

def read_graph_from_gcs(
    bucket: str,
    prefix: str,
    limit: Optional[int] = None,
    workers: int = 12,
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
        fail = 0
        for fut in as_completed(futures):
            try:
                pid, links = fut.result()
                outlinks[pid] = links
            except Exception as e:
                fail += 1
        print(f"[read_graph_from_gcs] failed downloads: {fail}/{len(object_names)}")


    # degrees
    for src in range(n):
        for dst in outlinks[src]:
            if 0 <= dst < n:
                in_degree[dst] += 1

    out_degree = {i: len(outlinks[i]) for i in range(n)}
    return outlinks, out_degree, in_degree
