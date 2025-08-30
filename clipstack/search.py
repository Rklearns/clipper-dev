"""
Search functionality for ClipStack.

This module provides fast and efficient search capabilities for clipboard
history using fuzzy matching and various search algorithms.
"""

from typing import List, Optional, Tuple
from rapidfuzz import fuzz, process
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .storage import ClipboardItem

console = Console()


class SearchManager:
    """
    Manages search operations for clipboard history.
    
    This class provides various search methods including fuzzy search,
    exact match, and content type filtering with fast performance.
    """
    
    def __init__(self):
        """Initialize the search manager."""
        pass
    
    def fuzzy_search(self, 
                    items: List[ClipboardItem], 
                    query: str, 
                    limit: Optional[int] = None,
                    threshold: int = 60) -> List[Tuple[ClipboardItem, float]]:
        """
        Perform fuzzy search on clipboard items.
        
        Args:
            items: List of ClipboardItem objects to search
            query: Search query string
            limit: Maximum number of results to return
            threshold: Minimum similarity score (0-100)
            
        Returns:
            List of tuples containing (ClipboardItem, similarity_score)
        """
        if not query.strip() or not items:
            return []
        
        # Use rapidfuzz for fast fuzzy search
        results = process.extract(
            query,
            [item.content for item in items],
            limit=limit or len(items),
            score_cutoff=threshold,
            scorer=fuzz.partial_ratio
        )
        
        # Map results back to ClipboardItem objects with scores
        search_results = []
        for content, score, index in results:
            search_results.append((items[index], score))
        
        return search_results
    
    def exact_search(self, 
                    items: List[ClipboardItem], 
                    query: str, 
                    case_sensitive: bool = False) -> List[ClipboardItem]:
        """
        Perform exact search on clipboard items.
        
        Args:
            items: List of ClipboardItem objects to search
            query: Search query string
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            List of matching ClipboardItem objects
        """
        if not query.strip() or not items:
            return []
        
        results = []
        search_query = query if case_sensitive else query.lower()
        
        for item in items:
            content = item.content if case_sensitive else item.content.lower()
            if search_query in content:
                results.append(item)
        
        return results
    
    def regex_search(self, 
                    items: List[ClipboardItem], 
                    pattern: str, 
                    case_sensitive: bool = False) -> List[ClipboardItem]:
        """
        Perform regex search on clipboard items.
        
        Args:
            items: List of ClipboardItem objects to search
            pattern: Regular expression pattern
            case_sensitive: Whether to perform case-sensitive search
            
        Returns:
            List of matching ClipboardItem objects
        """
        import re
        
        if not pattern or not items:
            return []
        
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            results = []
            
            for item in items:
                if regex.search(item.content):
                    results.append(item)
            
            return results
            
        except re.error as e:
            console.print(f"[red]Invalid regex pattern: {e}[/red]")
            return []
    
    def content_type_search(self, 
                           items: List[ClipboardItem], 
                           content_type: str) -> List[ClipboardItem]:
        """
        Search for items by content type.
        
        Args:
            items: List of ClipboardItem objects to search
            content_type: Content type to search for
            
        Returns:
            List of matching ClipboardItem objects
        """
        if not content_type or not items:
            return []
        
        content_type_lower = content_type.lower()
        return [item for item in items if content_type_lower in item.content_type.lower()]
    
    def advanced_search(self, 
                       items: List[ClipboardItem], 
                       query: str,
                       search_type: str = "fuzzy",
                       content_type: Optional[str] = None,
                       min_length: Optional[int] = None,
                       max_length: Optional[int] = None,
                       limit: Optional[int] = None) -> List[ClipboardItem]:
        """
        Perform advanced search with multiple filters.
        
        Args:
            items: List of ClipboardItem objects to search
            query: Search query string
            search_type: Type of search (fuzzy, exact, regex)
            content_type: Filter by content type
            min_length: Minimum content length
            max_length: Maximum content length
            limit: Maximum number of results
            
        Returns:
            List of matching ClipboardItem objects
        """
        # Start with all items
        results = items
        
        # Apply content type filter
        if content_type:
            results = self.content_type_search(results, content_type)
        
        # Apply length filters
        if min_length is not None:
            results = [item for item in results if item.content_length >= min_length]
        
        if max_length is not None:
            results = [item for item in results if item.content_length <= max_length]
        
        # Apply search query
        if query:
            if search_type == "fuzzy":
                search_results = self.fuzzy_search(results, query, limit)
                results = [item for item, _ in search_results]
            elif search_type == "exact":
                results = self.exact_search(results, query)
            elif search_type == "regex":
                results = self.regex_search(results, query)
            else:
                # Default to fuzzy search
                search_results = self.fuzzy_search(results, query, limit)
                results = [item for item, _ in search_results]
        
        # Apply limit
        if limit and len(results) > limit:
            results = results[:limit]
        
        return results
    
    def search_and_display(self, 
                          items: List[ClipboardItem], 
                          query: str,
                          search_type: str = "fuzzy",
                          max_preview_length: int = 80) -> None:
        """
        Perform search and display results in a formatted table.
        
        Args:
            items: List of ClipboardItem objects to search
            query: Search query string
            search_type: Type of search to perform
            max_preview_length: Maximum length for content preview
        """
        if not query.strip():
            console.print("[yellow]Please provide a search query[/yellow]")
            return
        
        # Perform search
        if search_type == "fuzzy":
            search_results = self.fuzzy_search(items, query)
            results = [item for item, _ in search_results]
        elif search_type == "exact":
            results = self.exact_search(items, query)
        elif search_type == "regex":
            results = self.regex_search(items, query)
        else:
            console.print(f"[red]Unknown search type: {search_type}[/red]")
            return
        
        if not results:
            console.print(f"[yellow]No results found for '{query}'[/yellow]")
            return
        
        # Display results
        self._display_search_results(results, query, search_type, max_preview_length)
    
    def _display_search_results(self, 
                              results: List[ClipboardItem], 
                              query: str,
                              search_type: str,
                              max_preview_length: int) -> None:
        """
        Display search results in a formatted table.
        
        Args:
            results: List of ClipboardItem objects to display
            query: Original search query
            search_type: Type of search performed
            max_preview_length: Maximum length for content preview
        """
        table = Table(title=f"🔍 Search Results for '{query}' ({search_type} search)")
        table.add_column("Index", style="cyan", justify="center")
        table.add_column("Score", style="yellow", justify="center")
        table.add_column("Timestamp", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Preview", style="white", max_width=max_preview_length)
        
        for i, item in enumerate(results):
            # Calculate similarity score for fuzzy search
            if search_type == "fuzzy":
                score = fuzz.partial_ratio(query.lower(), item.content.lower())
                score_str = f"{score:.1f}%"
            else:
                score_str = "N/A"
            
            # Format preview
            preview = item.content[:max_preview_length]
            if len(item.content) > max_preview_length:
                preview += "..."
            
            table.add_row(
                str(i),
                score_str,
                item.formatted_timestamp,
                item.content_type,
                preview
            )
        
        console.print(table)
        console.print(f"[green]Found {len(results)} result(s)[/green]")
    
    def get_search_suggestions(self, 
                              items: List[ClipboardItem], 
                              partial_query: str, 
                              limit: int = 5) -> List[str]:
        """
        Get search suggestions based on partial input.
        
        Args:
            items: List of ClipboardItem objects to search
            partial_query: Partial search query
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested search terms
        """
        if not partial_query.strip() or not items:
            return []
        
        # Find common patterns in content that start with the partial query
        suggestions = set()
        
        for item in items:
            words = item.content.lower().split()
            for word in words:
                if word.startswith(partial_query.lower()) and len(word) > len(partial_query):
                    suggestions.add(word)
                    if len(suggestions) >= limit:
                        break
            if len(suggestions) >= limit:
                break
        
        return sorted(list(suggestions))[:limit]
    
    def search_statistics(self, 
                         items: List[ClipboardItem], 
                         query: str) -> dict:
        """
        Get statistics about search results.
        
        Args:
            items: List of ClipboardItem objects searched
            query: Search query used
            
        Returns:
            Dictionary containing search statistics
        """
        if not query.strip():
            return {}
        
        # Perform fuzzy search to get scores
        search_results = self.fuzzy_search(items, query)
        
        if not search_results:
            return {
                "query": query,
                "total_results": 0,
                "average_score": 0,
                "best_score": 0,
                "worst_score": 0
            }
        
        scores = [score for _, score in search_results]
        
        return {
            "query": query,
            "total_results": len(search_results),
            "average_score": sum(scores) / len(scores),
            "best_score": max(scores),
            "worst_score": min(scores),
            "score_distribution": {
                "excellent": len([s for s in scores if s >= 90]),
                "good": len([s for s in scores if 70 <= s < 90]),
                "fair": len([s for s in scores if 50 <= s < 70]),
                "poor": len([s for s in scores if s < 50])
            }
        }
