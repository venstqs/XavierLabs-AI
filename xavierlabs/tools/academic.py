from typing import List, Dict, Any, Optional
import httpx
import arxiv
from duckduckgo_search import DDGS


class AcademicPaper:
    def __init__(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        year: Optional[int],
        url: str,
        source: str,
        citations: int = 0,
    ):
        self.title = title
        self.authors = authors
        self.abstract = abstract
        self.year = year
        self.url = url
        self.source = source
        self.citations = citations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "year": self.year,
            "url": self.url,
            "source": self.source,
            "citations": self.citations,
        }

    def format_summary(self) -> str:
        authors_str = ", ".join(self.authors[:3]) + (" et al." if len(self.authors) > 3 else "")
        return f"[{self.source.upper()}] {self.title} ({self.year or 'N/A'})\nAuthors: {authors_str}\nURL: {self.url}\nAbstract: {self.abstract[:400]}..."


class AcademicDiscoveryTool:
    """
    Unified academic literature search querying ArXiv, Semantic Scholar,
    and DuckDuckGo academic fallback.
    """

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    def search_arxiv(self, query: str, max_results: int = 5) -> List[AcademicPaper]:
        """Queries the official ArXiv API."""
        papers = []
        try:
            client = arxiv.Client(
                page_size=max_results,
                delay_seconds=1.0,
                num_retries=2
            )
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
            )
            for result in client.results(search):
                paper = AcademicPaper(
                    title=result.title,
                    authors=[a.name for a in result.authors],
                    abstract=result.summary.replace("\n", " ").strip(),
                    year=result.published.year if result.published else None,
                    url=result.entry_id,
                    source="arxiv",
                )
                papers.append(paper)
        except Exception as e:
            # ArXiv client might fail or timeout
            pass
        return papers

    def search_semantic_scholar(self, query: str, max_results: int = 5) -> List[AcademicPaper]:
        """Queries the public Semantic Scholar Graph API."""
        papers = []
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,authors,abstract,year,citationCount,url",
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    for item in data:
                        abstract = item.get("abstract") or "No abstract available."
                        authors = [a.get("name", "") for a in item.get("authors", [])]
                        papers.append(
                            AcademicPaper(
                                title=item.get("title", ""),
                                authors=authors,
                                abstract=abstract.replace("\n", " ").strip(),
                                year=item.get("year"),
                                url=item.get("url") or f"https://www.semanticscholar.org/paper/{item.get('paperId', '')}",
                                source="semantic_scholar",
                                citations=item.get("citationCount", 0) or 0,
                            )
                        )
        except Exception:
            pass
        return papers

    def search_web_fallback(self, query: str, max_results: int = 3) -> List[AcademicPaper]:
        """Fallback search using DuckDuckGo for papers / scientific blogs."""
        papers = []
        try:
            ddgs = DDGS()
            results = ddgs.text(f"{query} research paper arxiv pdf", max_results=max_results)
            for r in results:
                papers.append(
                    AcademicPaper(
                        title=r.get("title", ""),
                        authors=["Web Reference"],
                        abstract=r.get("body", ""),
                        year=None,
                        url=r.get("href", ""),
                        source="web",
                    )
                )
        except Exception:
            pass
        return papers

    def search(self, query: str, max_results: int = 6) -> List[AcademicPaper]:
        """
        Executes a combined search across ArXiv, Semantic Scholar, and Web.
        Deduplicates results by lowercase title.
        """
        results: List[AcademicPaper] = []
        seen_titles = set()

        # Step 1: ArXiv
        arxiv_results = self.search_arxiv(query, max_results=max_results // 2 + 1)
        for p in arxiv_results:
            key = p.title.strip().lower()
            if key not in seen_titles:
                seen_titles.add(key)
                results.append(p)

        # Step 2: Semantic Scholar
        ss_results = self.search_semantic_scholar(query, max_results=max_results // 2 + 1)
        for p in ss_results:
            key = p.title.strip().lower()
            if key not in seen_titles:
                seen_titles.add(key)
                results.append(p)

        # Step 3: If still sparse, use DDG fallback
        if len(results) < 2:
            ddg_results = self.search_web_fallback(query, max_results=3)
            for p in ddg_results:
                key = p.title.strip().lower()
                if key not in seen_titles:
                    seen_titles.add(key)
                    results.append(p)

        return results[:max_results]
