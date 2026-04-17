from typing import List, Optional
from src.models import UserProfile, Article
from src.agent import NewsAgent
from src.database import save_profile, load_profile

class NewsOrchestrator:
    """Manages the application state, agent coordination, and data persistence."""

    def __init__(self):
        self.agent = NewsAgent()
        self.profile: Optional[UserProfile] = None
        self.article_queue: List[Article] = []

    def load_existing_profile(self) -> bool:
        """Attempts to load a profile from the database."""
        self.profile = load_profile()
        return self.profile is not None

    def create_new_profile(self, topics: List[str]):
        """Initializes a new profile with starting topics."""
        self.profile = UserProfile(interests=topics)
        save_profile(self.profile)

    def seed_queue(self):
        """Initial seeding of the article queue based on interests."""
        if not self.profile:
            return
        
        seed_topics = self.profile.interests[:3]
        for topic in seed_topics:
            self.fetch_and_enqueue(topic)

    def fetch_and_enqueue(self, topic: str, priority: bool = False):
        """Fetches a new article and adds it to the queue."""
        article = self.agent.get_next_article(self.profile, topic)
        if priority:
            self.article_queue.insert(0, article)
        else:
            self.article_queue.append(article)

    def process_feedback(self, article: Article, liked: bool):
        """Updates the profile based on user feedback and persists changes."""
        article.score = 1 if liked else 0
        self.profile.history.append(article)
        
        # Agentic loop: update the refined bio
        self.profile.refined_bio = self.agent.update_profile(self.profile, article)
        save_profile(self.profile)
        
        # Auto-fetch next article based on rotated interests
        next_topic = self.profile.interests[len(self.profile.history) % len(self.profile.interests)]
        self.fetch_and_enqueue(next_topic)

    def get_next_article(self) -> Optional[Article]:
        """Retrieves the next article from the queue."""
        return self.article_queue.pop(0) if self.article_queue else None

    def add_new_topic(self, topic: str):
        """Adds a new interest and fetches an immediate result."""
        if topic not in self.profile.interests:
            self.profile.interests.append(topic)
        self.fetch_and_enqueue(topic, priority=True)