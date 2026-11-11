# KIT Math Search Engine

A small search engine for the website of the KIT Department of Mathematics (math.kit.edu).
It crawls the site, ranks pages with the PageRank algorithm and provides a desktop search interface.

Course project at KIT

## How it works

The project runs as a pipeline of three stages:

**1. Crawler** (`crawler.py`)
- Breadth-first crawl starting at `http://www.math.kit.edu`, up to a configurable link depth (default: 3)
- Stays within the domain (optionally including subdomains such as `didaktik.math.kit.edu`)
- Skips non-HTML resources (PDFs, images, office documents, media)
- Normalizes URLs (removes fragments and `index.html`/`index.php`, handles redirects) to avoid duplicate pages
- Extracts title and main text of each page, ignoring scripts, styles and navigation
- Builds the link graph between pages, removes pages without outgoing links and renumbers the remaining pages

**2. PageRank** (`PageRankAlgo.py`)
- Builds the link matrix A as a sparse column-stochastic matrix: column j distributes page j's rank equally over its outgoing links
- Computes the ranking vector as the stationary distribution of the Google matrix

  M = (1 − m) · A + (m / N) · 1·1ᵀ, with damping parameter m = 0.15 and N pages

- Uses power iteration (up to 1000 iterations, stopping when the L1 change falls below 10⁻⁸)

**3. Search and GUI** (`searching_engine.py`, `gui_app.py`)
- A page matches if every word of the query appears in its text or title (case-insensitive)
- Matching pages are sorted by their PageRank score
- Each result shows title (clickable), PageRank score, URL and a text snippet around the first query word
- Desktop interface built with PySide6 (Qt)

## Project structure

| File | Purpose |
|---|---|
| `main.py` | Entry point: runs crawler and PageRank if no data exists yet, then starts the GUI |
| `crawler.py` | Crawling, text and link extraction, saving results as JSON |
| `PageRankAlgo.py` | PageRank computation |
| `loader.py` | Loads the JSON files and combines them per page |
| `searching_engine.py` | Query matching, snippets, ranking |
| `gui_app.py` | Search window |

Generated data files: `pages.json`, `titles.json`, `texts.json`, `links.json`, `ranks.json`.
Delete them to crawl again from scratch.

## Run locally

```bash
pip install -r requirements.txt
python main.py
```

The first start crawls the website and may take a few minutes. Later starts load the saved data directly.

## Limitations

- **Ranking ignores relevance:** results are ordered by PageRank only, so an important page that mentions the query once ranks above a less linked page that is entirely about it. Combining PageRank with a text relevance score such as TF-IDF would address this.
- **Substring matching:** queries match parts of words (e.g. "rank" also matches "Frank").
- **Pages without outgoing links are removed** from the graph and therefore cannot be found.
- **Limited crawl depth:** with depth 3, deeper pages of the site are not indexed.
