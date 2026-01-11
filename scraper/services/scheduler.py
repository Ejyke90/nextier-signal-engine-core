import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scraper.utils import get_logger, Config
from scraper.services.scraping_service import ScrapingService
from scraper.services.message_broker import MessageBrokerService
from scraper.repositories.mongodb_repository import MongoDBRepository

logger = get_logger(__name__)


class AutomationScheduler:
    """Background scheduler for automated scraping tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='UTC')
        self.scraping_service: Optional[ScrapingService] = None
        self.mongodb_repo: Optional[MongoDBRepository] = None
        self.message_broker: Optional[MessageBrokerService] = None
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.is_running = False
        self.automation_log_path = Path("/data/automation_logs.json")
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure automation log file exists"""
        try:
            self.automation_log_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.automation_log_path.exists():
                self.automation_log_path.write_text(json.dumps([], indent=2))
                logger.info("Created automation log file", path=str(self.automation_log_path))
        except Exception as e:
            logger.warning("Could not create automation log file", error=str(e))
    
    def _log_automation_event(self, event_type: str, status: str, details: dict):
        """Log automation events to file"""
        try:
            logs = []
            if self.automation_log_path.exists():
                logs = json.loads(self.automation_log_path.read_text())
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "status": status,
                "details": details
            }
            logs.append(log_entry)
            
            # Keep only last 100 entries
            logs = logs[-100:]
            
            self.automation_log_path.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error("Failed to write automation log", error=str(e))
    
    async def _scrape_job(self):
        """Async scraping job that runs on schedule"""
        if self.is_running:
            logger.warning("Scraping job already running, skipping this cycle")
            return
        
        self.is_running = True
        start_time = datetime.now()
        
        try:
            logger.info("🤖 Automated scraping job started")
            
            # Initialize services if not already done
            if not self.scraping_service:
                self.scraping_service = ScrapingService()
            if not self.mongodb_repo:
                self.mongodb_repo = MongoDBRepository()
            if not self.message_broker:
                self.message_broker = MessageBrokerService()
            
            # Perform scraping
            articles = await self.scraping_service.scrape_multiple_sources()
            
            if not articles:
                logger.warning("No articles scraped in automated job")
                self._log_automation_event(
                    "scheduled_scrape",
                    "warning",
                    {"articles_count": 0, "message": "No articles scraped"}
                )
                return
            
            # Save to MongoDB
            db_success = self.mongodb_repo.save_articles(articles)
            
            # Publish to message broker
            mq_success = self.message_broker.publish_articles(articles)
            
            # Check for high-risk articles (>85) and trigger webhooks
            high_risk_articles = [a for a in articles if a.get('risk_score', 0) > 85]
            
            if high_risk_articles:
                logger.warning(
                    f"🚨 {len(high_risk_articles)} HIGH-RISK articles detected (risk_score > 85)",
                    articles=[a.get('title', 'Unknown')[:50] for a in high_risk_articles]
                )
                # Trigger webhook notification (will be implemented in deduplication service)
                self._trigger_high_risk_webhook(high_risk_articles)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.last_run = start_time
            
            logger.info(
                "✅ Automated scraping job completed",
                articles_scraped=len(articles),
                high_risk_count=len(high_risk_articles),
                duration_seconds=duration,
                db_success=db_success,
                mq_success=mq_success
            )
            
            self._log_automation_event(
                "scheduled_scrape",
                "success",
                {
                    "articles_count": len(articles),
                    "high_risk_count": len(high_risk_articles),
                    "duration_seconds": duration,
                    "db_success": db_success,
                    "mq_success": mq_success
                }
            )
            
        except Exception as e:
            logger.error("❌ Automated scraping job failed", error=str(e))
            self._log_automation_event(
                "scheduled_scrape",
                "error",
                {"error": str(e)}
            )
        finally:
            self.is_running = False
    
    def _trigger_high_risk_webhook(self, articles: list):
        """Trigger webhook for high-risk articles"""
        try:
            webhook_data = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": "high_risk_articles",
                "count": len(articles),
                "articles": [
                    {
                        "title": a.get('title', 'Unknown'),
                        "source": a.get('source', 'Unknown'),
                        "risk_score": a.get('risk_score', 0),
                        "url": a.get('url', '')
                    }
                    for a in articles[:5]  # Limit to top 5
                ]
            }
            
            # Write to webhook file for UI to pick up
            webhook_path = Path("/data/high_risk_alerts.json")
            webhook_path.parent.mkdir(parents=True, exist_ok=True)
            
            existing_alerts = []
            if webhook_path.exists():
                existing_alerts = json.loads(webhook_path.read_text())
            
            existing_alerts.append(webhook_data)
            # Keep only last 20 alerts
            existing_alerts = existing_alerts[-20:]
            
            webhook_path.write_text(json.dumps(existing_alerts, indent=2))
            logger.info("High-risk webhook triggered", alert_count=len(articles))
            
        except Exception as e:
            logger.error("Failed to trigger high-risk webhook", error=str(e))
    
    def _sync_scrape_job(self):
        """Synchronous wrapper for async scraping job"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._scrape_job())
            loop.close()
        except Exception as e:
            logger.error("Error in sync scrape job wrapper", error=str(e))
    
    def start(self):
        """Start the background scheduler with 15-minute cron trigger"""
        try:
            # Schedule scraping every 15 minutes
            self.scheduler.add_job(
                self._sync_scrape_job,
                trigger=CronTrigger(minute='*/15'),  # Every 15 minutes
                id='automated_scraping',
                name='Automated News Scraping',
                replace_existing=True,
                max_instances=1
            )
            
            self.scheduler.start()
            
            # Get next run time
            job = self.scheduler.get_job('automated_scraping')
            if job:
                self.next_run = job.next_run_time
            
            logger.info(
                "🚀 Automation scheduler started",
                schedule="Every 15 minutes",
                next_run=self.next_run.isoformat() if self.next_run else "Unknown"
            )
            
            self._log_automation_event(
                "scheduler_start",
                "success",
                {
                    "schedule": "*/15 * * * *",
                    "next_run": self.next_run.isoformat() if self.next_run else None
                }
            )
            
        except Exception as e:
            logger.error("Failed to start automation scheduler", error=str(e))
            raise
    
    def stop(self):
        """Stop the background scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
                logger.info("Automation scheduler stopped")
                
                self._log_automation_event(
                    "scheduler_stop",
                    "success",
                    {"last_run": self.last_run.isoformat() if self.last_run else None}
                )
        except Exception as e:
            logger.error("Error stopping scheduler", error=str(e))
    
    def get_status(self) -> dict:
        """Get current scheduler status"""
        job = self.scheduler.get_job('automated_scraping')
        return {
            "scheduler_running": self.scheduler.running,
            "job_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": job.next_run_time.isoformat() if job and job.next_run_time else None,
            "schedule": "Every 15 minutes (*/15 * * * *)"
        }
