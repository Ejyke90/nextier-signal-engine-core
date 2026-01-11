import hashlib
from typing import Dict, List, Any, Set

from scraper.utils import get_logger

logger = get_logger(__name__)


class DeduplicationService:
    """Service for deduplicating articles based on SHA-256 fingerprinting and calculating veracity scores."""

    @staticmethod
    def generate_fingerprint(content: str) -> str:
        """
        Generate a SHA-256 fingerprint for the given content.

        Args:
            content: The content to fingerprint (e.g., article title + content)

        Returns:
            A hexadecimal string representing the SHA-256 hash
        """
        if not content:
            return ""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    @staticmethod
    def deduplicate_and_score(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate articles based on fingerprint and assign veracity scores.

        Args:
            articles: List of article dictionaries to process

        Returns:
            Deduplicated list of articles with updated veracity scores
        """
        if not articles:
            return []

        # Dictionary to store articles by fingerprint
        fingerprint_to_articles: Dict[str, List[Dict[str, Any]]] = {}
        processed_fingerprints: Set[str] = set()

        for article in articles:
            # Generate fingerprint if not already present
            if 'fingerprint' not in article or not article['fingerprint']:
                content = article.get('title', '') + article.get('content', '')
                article['fingerprint'] = DeduplicationService.generate_fingerprint(content)
            
            fingerprint = article['fingerprint']
            if fingerprint:
                if fingerprint not in fingerprint_to_articles:
                    fingerprint_to_articles[fingerprint] = []
                fingerprint_to_articles[fingerprint].append(article)
                processed_fingerprints.add(fingerprint)

        # Deduplicate and calculate veracity scores
        deduplicated_articles = []
        for fingerprint in processed_fingerprints:
            related_articles = fingerprint_to_articles[fingerprint]
            source_count = len(set(article['source'] for article in related_articles))
            
            # Calculate veracity score based on number of unique sources
            # Simple formula: base score of 0.5 per source, capped at 1.0
            veracity_score = min(1.0, source_count * 0.5)
            
            # Take the first article as the representative one (could be enhanced to pick the most detailed)
            primary_article = related_articles[0].copy()
            primary_article['veracity_score'] = veracity_score
            primary_article['source_count'] = source_count
            
            # If there are multiple sources, log for verification
            if source_count > 1:
                sources = [article['source'] for article in related_articles]
                logger.info(f"Duplicate article detected across {source_count} sources", 
                            title=primary_article['title'][:50], sources=sources)
                # Optionally flag for verification if veracity is below a threshold
                if 'features' in primary_article:
                    primary_article['features']['verification_needed'] = veracity_score < 0.8
            
            deduplicated_articles.append(primary_article)

        logger.info(f"Deduplication complete: {len(articles)} articles reduced to {len(deduplicated_articles)} unique entries")
        return deduplicated_articles
