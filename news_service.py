import requests
import os
import logging
from datetime import datetime

class NewsService:
    def __init__(self):
        self.api_key = os.environ.get("NEWS_API_KEY", "default_key")
        self.base_url = "https://newsapi.org/v2"
        
    def get_top_headlines(self, category=None, country='us', page=1, page_size=20):
        """Fetch top headlines from NewsAPI"""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                'apiKey': self.api_key,
                'country': country,
                'page': page,
                'pageSize': page_size
            }
            
            if category:
                params['category'] = category
                
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'ok':
                return self._format_articles(data['articles'])
            else:
                logging.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            logging.error(f"Error fetching news: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []
    
    def search_news(self, query, page=1, page_size=20):
        """Search for news articles"""
        try:
            url = f"{self.base_url}/everything"
            params = {
                'apiKey': self.api_key,
                'q': query,
                'page': page,
                'pageSize': page_size,
                'sortBy': 'publishedAt'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data['status'] == 'ok':
                return self._format_articles(data['articles'])
            else:
                logging.error(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            logging.error(f"Error searching news: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return []
    
    def _format_articles(self, articles):
        """Format articles from NewsAPI response"""
        formatted_articles = []
        
        for article in articles:
            # Skip articles with incomplete data
            if not article.get('title') or article.get('title') == '[Removed]':
                continue
                
            formatted_article = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'author': article.get('author', 'Unknown'),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'url': article.get('url', ''),
                'image_url': article.get('urlToImage', ''),
                'published_at': self._parse_date(article.get('publishedAt')),
                'is_custom': False
            }
            formatted_articles.append(formatted_article)
            
        return formatted_articles
    
    def _parse_date(self, date_string):
        """Parse date string from NewsAPI"""
        if not date_string:
            return datetime.utcnow()
            
        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except:
            return datetime.utcnow()

# Global instance
news_service = NewsService()
