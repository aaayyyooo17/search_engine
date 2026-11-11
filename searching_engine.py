from concurrent.futures import ThreadPoolExecutor
import os
from loader import combined
def snippet(request, text, N):
    req_startindex=text.lower().find(request.lower())
    if req_startindex==-1:
        return None
    else:
        if req_startindex-N<0:
            snip_start=0
        else:
            snip_start=req_startindex-N
        if req_startindex+len(request)+N>len(text):
            snip_end=len(text)
        else:
            snip_end=req_startindex+len(request)+N
        snippet=text[snip_start:snip_end]
        return snippet
   
def _process_single_page(args):
  url, page, request_words = args
  text_raw = page["text"]
  text_lower = text_raw.lower()
  title_lower = page["title"].lower()

  if all(word in text_lower or word in title_lower for word in request_words):
    page_snippet = snippet(request_words[0], text_raw, 120)
    return {
        "url": url,
        "title": page["title"],
        "snippet": page_snippet,
        "weight": page["weight"],
    }

  return None


def search_and_rank_parallel(request, combined_data, max_workers= 4):
  request_words = request.lower().split()
  if not request_words:
    return []

  tasks = [(url, page, request_words) for url, page in combined_data.items()]

  results = []

  with ThreadPoolExecutor(max_workers=max_workers) as executor:
    mapped_results = executor.map(_process_single_page, tasks)
    for res in mapped_results:
      if res is not None:
        results.append(res)
  results.sort(key=lambda item: item["weight"], reverse=True)
  return results
