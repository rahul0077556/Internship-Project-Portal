import os
from typing import List, Dict, Any

from apify_client import ApifyClient


def _get_client() -> ApifyClient:
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN not set")
    return ApifyClient(token)


def fetch_linkedin_jobs(keywords: List[str], location: str = "India", rows: int = 30) -> List[Dict[str, Any]]:
    """Fetch jobs from Apify LinkedIn Jobs Scraper actor."""
    if not keywords:
        return []
    client = _get_client()
    title_query = ", ".join(keywords[:5])
    run_input = {
        "title": title_query,
        "location": location,
        "rows": rows,
        "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }
    run = client.actor("BHzefUZlZRKWxkTck").call(run_input=run_input)
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(
            {
                "title": item.get("title"),
                "company_name": item.get("companyName"),
                "location": item.get("location"),
                "url": item.get("jobUrl"),
                "description": item.get("description"),
                "source": "linkedin",
            }
        )
    return results


def fetch_naukri_jobs(keywords: List[str], max_items: int = 30) -> List[Dict[str, Any]]:
    """Fetch jobs from Apify Naukri scraper actor."""
    if not keywords:
        return []
    client = _get_client()
    # Build simple search URLs for top keywords
    search_urls = [f"https://www.naukri.com/{kw.replace(' ', '-')}-jobs" for kw in keywords[:3]]
    run_input = {
        "searchUrls": search_urls,
        "maxItems": max_items,
        "proxyConfiguration": {"useApifyProxy": False},
    }
    run = client.actor("wsrn5gy5C4EDeYCcD").call(run_input=run_input)
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(
            {
                "title": item.get("title"),
                "company_name": item.get("company"),
                "location": item.get("location"),
                "url": item.get("url"),
                "description": item.get("description"),
                "source": "naukri",
            }
        )
    return results


def fetch_jobs_from_apify(keywords: List[str], location: str = "India") -> List[Dict[str, Any]]:
    """Aggregate jobs from multiple Apify actors."""
    linkedin_jobs = fetch_linkedin_jobs(keywords, location=location, rows=30)
    naukri_jobs = fetch_naukri_jobs(keywords, max_items=30)
    # De-duplicate by title + company + source
    seen = set()
    deduped = []
    for job in linkedin_jobs + naukri_jobs:
        key = (job.get("title"), job.get("company_name"), job.get("source"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)
    return deduped

