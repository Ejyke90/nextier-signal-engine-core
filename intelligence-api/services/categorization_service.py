import asyncio
from datetime import datetime
from typing import Dict, Any
from ..utils import get_logger, Config
from ..repositories import MongoDBRepository
from ..services import LLMProcessor

logger = get_logger(__name__)


class CategorizationService:
    def __init__(self, mongodb_repo: MongoDBRepository, llm_processor: LLMProcessor):
        self.mongodb_repo = mongodb_repo
        self.llm_processor = llm_processor
        self._running = False
    
    async def categorize_articles(self) -> Dict[str, Any]:
        """Main categorization function - categorize uncategorized articles"""
        try:
            logger.info("Starting article categorization cycle")
            
            # Get uncategorized articles
            uncategorized_articles = self.mongodb_repo.get_uncategorized_articles()
            
            if not uncategorized_articles:
                logger.info("No uncategorized articles found")
                return {
                    "status": "success",
                    "articles_categorized": 0,
                    "message": "No new articles to categorize"
                }
            
            logger.info("Categorizing articles", count=len(uncategorized_articles))
            
            # Categorize articles with LLM
            categorized_results = await self.llm_processor.categorize_articles_batch(uncategorized_articles)
            
            if categorized_results:
                # Update articles in DB
                success_count = 0
                for result in categorized_results:
                    success = self.mongodb_repo.update_article_category(result["id"], result["category"], result["confidence"])
                    if success:
                        success_count += 1
                
                if success_count > 0:
                    logger.info("Successfully categorized articles", count=success_count)
                    return {
                        "status": "success",
                        "articles_categorized": success_count,
                        "message": f"Successfully categorized {success_count} articles"
                    }
                else:
                    logger.warning("No articles were successfully categorized")
                    return {
                        "status": "warning",
                        "articles_categorized": 0,
                        "message": "No articles were successfully categorized"
                    }
            else:
                logger.warning("No categorization results were obtained")
                return {
                    "status": "warning",
                    "articles_categorized": 0,
                    "message": "No categorization results were obtained"
                }
                
        except Exception as e:
            logger.error("Error in categorization cycle", error=str(e))
            return {
                "status": "error",
                "articles_categorized": 0,
                "message": f"Categorization failed: {str(e)}"
            }
    
    async def start_background_categorizer(self) -> None:
        """Start background categorization loop every 5 minutes"""
        self._running = True
        logger.info("Starting background categorizer")
        
        while self._running:
            try:
                result = await self.categorize_articles()
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error("Error in background categorizer", error=str(e))
                await asyncio.sleep(300)
    
    def stop_background_categorizer(self) -> None:
        """Stop background categorization loop"""
        self._running = False
        logger.info("Stopping background categorizer")
