"""
Dive Search Processor - Query parsing and semantic understanding

Part of Dive Search Engine - processes and understands search queries.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum


class QueryType(Enum):
    """Types of search queries"""
    FILE = "file"
    MEMORY = "memory"
    UPDATE = "update"
    DEPENDENCY = "dependency"
    MIXED = "mixed"


class QueryIntent(Enum):
    """Intent of search query"""
    FIND = "find"  # Find files/sections
    ANALYZE = "analyze"  # Analyze dependencies/impact
    TRACK = "track"  # Track changes
    UNDERSTAND = "understand"  # Understand code/docs


class ParsedQuery:
    """Parsed search query"""
    
    def __init__(self, original: str):
        self.original = original
        self.query_type = QueryType.MIXED
        self.intent = QueryIntent.FIND
        self.keywords: List[str] = []
        self.filters: Dict = {}
        self.sources: List[str] = []
        self.semantic: bool = False
        self.expanded_keywords: Set[str] = set()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "original": self.original,
            "query_type": self.query_type.value,
            "intent": self.intent.value,
            "keywords": self.keywords,
            "filters": self.filters,
            "sources": self.sources,
            "semantic": self.semantic,
            "expanded_keywords": list(self.expanded_keywords)
        }


class DiveSearchProcessor:
    """
    Process and understand search queries
    
    Features:
    - Parse natural language queries
    - Detect query type and intent
    - Extract keywords and filters
    - Expand queries with synonyms
    - Semantic understanding (AI-powered)
    """
    
    def __init__(self):
        # Keyword synonyms for query expansion
        self.synonyms = {
            'orchestrator': ['routing', 'task_management', 'dispatcher', 'coordinator'],
            'memory': ['storage', 'persistence', 'data', 'state'],
            'coder': ['code_generation', 'programming', 'developer'],
            'update': ['change', 'modification', 'patch', 'upgrade'],
            'dependency': ['import', 'require', 'relationship', 'connection'],
            'search': ['find', 'lookup', 'query', 'index'],
            'breaking': ['incompatible', 'major_change', 'api_change']
        }
        
        # Intent keywords
        self.intent_keywords = {
            QueryIntent.FIND: ['find', 'search', 'locate', 'get', 'show', 'list'],
            QueryIntent.ANALYZE: ['analyze', 'check', 'inspect', 'examine', 'review'],
            QueryIntent.TRACK: ['track', 'history', 'changes', 'log', 'changelog'],
            QueryIntent.UNDERSTAND: ['understand', 'explain', 'what', 'how', 'why']
        }
        
        # Source keywords
        self.source_keywords = {
            'file': ['file', 'code', 'python', 'class', 'function'],
            'memory': ['memory', 'documentation', 'docs', 'full', 'criteria', 'changelog'],
            'update': ['update', 'change', 'breaking', 'version'],
            'dependency': ['dependency', 'dependent', 'import', 'relationship']
        }
    
    def parse_query(self, query: str) -> ParsedQuery:
        """
        Parse search query
        
        Args:
            query: Search query string
            
        Returns:
            ParsedQuery object
        """
        parsed = ParsedQuery(query)
        
        # Detect structured query (key:value format)
        if ':' in query and any(op in query for op in ['=', '>', '<']):
            self._parse_structured_query(parsed, query)
        else:
            self._parse_natural_query(parsed, query)
        
        # Expand keywords
        self._expand_keywords(parsed)
        
        return parsed
    
    def _parse_structured_query(self, parsed: ParsedQuery, query: str) -> None:
        """Parse structured query with filters"""
        # Extract filters (key:value or key=value)
        filter_pattern = r'(\w+)[:=](["\']?)([^"\'\s]+)\2'
        matches = re.findall(filter_pattern, query)
        
        for key, _, value in matches:
            key_lower = key.lower()
            
            # Map to filter categories
            if key_lower in ['type', 'file_type', 'filetype']:
                parsed.filters['file_type'] = value
            elif key_lower in ['source', 'src']:
                parsed.sources.append(value)
            elif key_lower in ['breaking', 'break']:
                parsed.filters['breaking'] = value.lower() in ['true', 'yes', '1']
            elif key_lower in ['version', 'ver', 'v']:
                parsed.filters['version'] = value
            elif key_lower in ['category', 'cat']:
                parsed.filters['category'] = value.upper()
            elif key_lower in ['project', 'proj']:
                parsed.filters['project'] = value
            elif key_lower in ['imports', 'import']:
                parsed.filters['imports'] = value
            elif key_lower in ['class', 'cls']:
                parsed.filters['has_class'] = value
            elif key_lower in ['function', 'func', 'fn']:
                parsed.filters['has_function'] = value
        
        # Extract remaining keywords
        query_without_filters = re.sub(filter_pattern, '', query)
        parsed.keywords = [w.strip() for w in query_without_filters.split() if w.strip()]
    
    def _parse_natural_query(self, parsed: ParsedQuery, query: str) -> None:
        """Parse natural language query"""
        query_lower = query.lower()
        
        # Detect intent
        for intent, keywords in self.intent_keywords.items():
            if any(kw in query_lower for kw in keywords):
                parsed.intent = intent
                break
        
        # Detect sources
        for source, keywords in self.source_keywords.items():
            if any(kw in query_lower for kw in keywords):
                if source not in parsed.sources:
                    parsed.sources.append(source)
        
        # If no sources detected, search all
        if not parsed.sources:
            parsed.sources = ['file', 'memory', 'update']
        
        # Detect query type
        if len(parsed.sources) == 1:
            parsed.query_type = QueryType[parsed.sources[0].upper()]
        else:
            parsed.query_type = QueryType.MIXED
        
        # Extract keywords (words longer than 2 chars, excluding common words)
        common_words = {'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'will', 'your', 'can', 'are', 'not', 'but', 'all', 'were', 'when', 'there', 'been', 'has', 'had', 'more', 'than', 'into', 'could', 'would', 'should', 'what', 'how', 'why', 'where'}
        
        words = re.findall(r'\b[a-zA-Z_]{3,}\b', query)
        parsed.keywords = [w for w in words if w.lower() not in common_words]
        
        # Detect semantic search indicators
        semantic_indicators = ['explain', 'understand', 'how', 'why', 'what is', 'describe']
        if any(ind in query_lower for ind in semantic_indicators):
            parsed.semantic = True
    
    def _expand_keywords(self, parsed: ParsedQuery) -> None:
        """Expand keywords with synonyms"""
        expanded = set(parsed.keywords)
        
        for keyword in parsed.keywords:
            keyword_lower = keyword.lower()
            
            # Add synonyms
            if keyword_lower in self.synonyms:
                expanded.update(self.synonyms[keyword_lower])
            
            # Add variations
            # e.g., "orchestrator" -> "orchestrate", "orchestration"
            if keyword_lower.endswith('or'):
                expanded.add(keyword_lower[:-2] + 'e')  # orchestrate
                expanded.add(keyword_lower[:-2] + 'ion')  # orchestration
            elif keyword_lower.endswith('er'):
                expanded.add(keyword_lower[:-2])  # code from coder
        
        parsed.expanded_keywords = expanded
    
    def understand_query(self, query: str) -> Dict:
        """
        Understand query with semantic analysis
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with understanding
        """
        parsed = self.parse_query(query)
        
        # Analyze query structure
        understanding = {
            "parsed": parsed.to_dict(),
            "suggestions": [],
            "clarifications": []
        }
        
        # Provide suggestions based on query
        if parsed.intent == QueryIntent.FIND:
            if 'file' in parsed.sources:
                understanding["suggestions"].append("Searching Python files with AST analysis")
            if 'memory' in parsed.sources:
                understanding["suggestions"].append("Searching memory documentation")
        
        elif parsed.intent == QueryIntent.ANALYZE:
            understanding["suggestions"].append("Will analyze dependencies and impact")
            if 'dependency' not in parsed.sources:
                parsed.sources.append('dependency')
        
        elif parsed.intent == QueryIntent.TRACK:
            if 'update' not in parsed.sources:
                parsed.sources.append('update')
            understanding["suggestions"].append("Searching change history")
        
        # Check for ambiguities
        if not parsed.keywords and not parsed.filters:
            understanding["clarifications"].append("Query is too broad, consider adding keywords or filters")
        
        if len(parsed.sources) > 2 and not parsed.semantic:
            understanding["clarifications"].append("Searching multiple sources, results may be diverse")
        
        return understanding
    
    def suggest_filters(self, query: str) -> List[Dict]:
        """
        Suggest filters based on query
        
        Args:
            query: Search query
            
        Returns:
            List of suggested filters
        """
        suggestions = []
        query_lower = query.lower()
        
        # Suggest file type filter
        if any(word in query_lower for word in ['python', 'code', 'class', 'function']):
            suggestions.append({
                "filter": "file_type",
                "value": "python",
                "reason": "Query mentions Python code"
            })
        
        # Suggest breaking filter
        if any(word in query_lower for word in ['breaking', 'incompatible', 'major']):
            suggestions.append({
                "filter": "breaking",
                "value": "true",
                "reason": "Query mentions breaking changes"
            })
        
        # Suggest version filter
        version_match = re.search(r'v?(\d+\.\d+(?:\.\d+)?)', query)
        if version_match:
            suggestions.append({
                "filter": "version",
                "value": version_match.group(1),
                "reason": f"Query mentions version {version_match.group(1)}"
            })
        
        return suggestions
    
    def build_search_params(self, query: str) -> Dict:
        """
        Build search parameters from query
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search parameters
        """
        parsed = self.parse_query(query)
        
        # Build search string from keywords and expanded keywords
        search_terms = list(parsed.expanded_keywords) if parsed.expanded_keywords else parsed.keywords
        search_string = ' '.join(search_terms) if search_terms else query
        
        return {
            "query": search_string,
            "sources": parsed.sources if parsed.sources else None,
            "filters": parsed.filters if parsed.filters else None,
            "semantic": parsed.semantic,
            "original_query": query,
            "query_type": parsed.query_type.value,
            "intent": parsed.intent.value
        }


if __name__ == "__main__":
    # Test search processor
    processor = DiveSearchProcessor()
    
    print("=== Testing Query Parsing ===\n")
    
    # Test natural language queries
    test_queries = [
        "find orchestrator routing logic",
        "show breaking changes in v21.0",
        "files that import dive_memory",
        "explain how memory system works",
        "class:DiveMemory type:python",
        "breaking:true version:21.0",
        "analyze dependencies of orchestrator"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        parsed = processor.parse_query(query)
        print(f"  Type: {parsed.query_type.value}")
        print(f"  Intent: {parsed.intent.value}")
        print(f"  Keywords: {parsed.keywords}")
        print(f"  Sources: {parsed.sources}")
        print(f"  Filters: {parsed.filters}")
        print(f"  Semantic: {parsed.semantic}")
        print(f"  Expanded: {list(parsed.expanded_keywords)[:5]}")
        print()
    
    # Test understanding
    print("=== Testing Query Understanding ===\n")
    query = "find files affected by memory change"
    understanding = processor.understand_query(query)
    print(f"Query: {query}")
    print(f"Suggestions: {understanding['suggestions']}")
    print(f"Clarifications: {understanding['clarifications']}")
    print()
    
    # Test filter suggestions
    print("=== Testing Filter Suggestions ===\n")
    query = "breaking changes in python files for v21.0"
    suggestions = processor.suggest_filters(query)
    print(f"Query: {query}")
    for sug in suggestions:
        print(f"  {sug['filter']}={sug['value']} - {sug['reason']}")
    print()
    
    # Test search params building
    print("=== Testing Search Params ===\n")
    query = "orchestrator routing with breaking changes"
    params = processor.build_search_params(query)
    print(f"Query: {query}")
    print(f"Params: {params}")
