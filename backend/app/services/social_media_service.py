"""Service for fetching real social media posts from Alzheimer's organizations."""
import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import logging

logger = logging.getLogger(__name__)


class SocialMediaService:
    """Service to fetch and cache social media posts from RSS feeds."""
    
    # RSS feeds from major Alzheimer's organizations and social media
    RSS_FEEDS = {
        'alzheimers_association': {
            'url': 'https://www.alz.org/news/rss',
            'name': "Alzheimer's Association",
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/alz.org'
        },
        'nia': {
            'url': 'https://www.nia.nih.gov/news/rss',
            'name': 'National Institute on Aging',
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/nia.nih.gov'
        },
        'alzheimers_research_uk': {
            'url': 'https://www.alzheimersresearchuk.org/feed/',
            'name': "Alzheimer's Research UK",
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/alzheimersresearchuk.org'
        },
        'alzheimers_society': {
            'url': 'https://www.alzheimers.org.uk/news/rss.xml',
            'name': "Alzheimer's Society",
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/alzheimers.org.uk'
        },
        'mayo_clinic': {
            'url': 'https://newsnetwork.mayoclinic.org/category/research/feed/',
            'name': 'Mayo Clinic Research',
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/mayoclinic.org'
        },
        'alzheimers_foundation': {
            'url': 'https://www.alzfdn.org/feed/',
            'name': "Alzheimer's Foundation of America",
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/alzfdn.org'
        },
        'bright_focus': {
            'url': 'https://www.brightfocus.org/alzheimers/feed',
            'name': 'BrightFocus Foundation',
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/brightfocus.org'
        },
        'usagainstalzheimers': {
            'url': 'https://www.usagainstalzheimers.org/feed',
            'name': 'UsAgainstAlzheimers',
            'platform': 'website',
            'logo': 'https://logo.clearbit.com/usagainstalzheimers.org'
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_duration = timedelta(hours=1)  # Refresh every hour for daily updates
    
    def fetch_posts(self, limit: int = 20) -> List[Dict]:
        """
        Fetch latest posts from RSS feeds.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of post dictionaries
        """
        all_posts = []
        
        for feed_key, feed_info in self.RSS_FEEDS.items():
            try:
                posts = self._fetch_from_feed(feed_info)
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Error fetching from {feed_key}: {e}")
                continue
        
        # Sort by date and limit
        all_posts.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_posts[:limit]
    
    def _fetch_from_feed(self, feed_info: Dict) -> List[Dict]:
        """Fetch posts from a single RSS feed."""
        posts = []
        
        try:
            feed = feedparser.parse(feed_info['url'])
            
            for entry in feed.entries[:10]:  # Get up to 10 from each feed
                # Parse date
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    timestamp = datetime(*published[:6])
                else:
                    timestamp = datetime.now()
                
                # Extract content
                content = entry.get('summary', entry.get('description', ''))
                # Clean HTML tags if present
                content = self._clean_html(content)
                
                post = {
                    'id': entry.get('id', entry.get('link', '')),
                    'platform': feed_info['platform'],
                    'author': feed_info['name'],
                    'handle': f"@{feed_info['name'].replace(' ', '').replace("'", '')}",
                    'avatar': feed_info.get('logo', ''),
                    'content': content[:500],
                    'url': entry.get('link', ''),
                    'timestamp': timestamp
                }
                
                posts.append(post)
                
        except Exception as e:
            logger.error(f"Error parsing feed {feed_info['url']}: {e}")
        
        return posts
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()
    
    def _get_avatar_emoji(self, name: str) -> str:
        """Get emoji avatar based on organization name."""
        if 'Research' in name:
            return '🔬'
        elif 'Institute' in name or 'National' in name:
            return '🏛️'
        elif 'Association' in name:
            return '🧠'
        else:
            return '💙'
    
    def format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp as relative time."""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 7:
            return timestamp.strftime('%b %d, %Y')
        elif diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"


def get_social_media_posts(db: Session, limit: int = 20) -> List[Dict]:
    """
    Get social media posts with caching.
    
    Args:
        db: Database session
        limit: Maximum number of posts
        
    Returns:
        List of formatted posts
    """
    service = SocialMediaService(db)
    posts = service.fetch_posts(limit)
    
    # Format timestamps
    for post in posts:
        post['timestamp_formatted'] = service.format_timestamp(post['timestamp'])
        post['timestamp'] = post['timestamp'].isoformat()
    
    return posts
