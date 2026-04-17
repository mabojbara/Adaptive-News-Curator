from pydantic import BaseModel, Field
from typing import List, Optional

class Article(BaseModel):
    """Information about a curated news article."""
    title: str = Field(description="The title of the news article")
    url: str = Field(description="The source URL of the article")
    summary: str = Field(description="A 2-3 sentence summary of the article")
    tags: List[str] = Field(description="A list of 2-3 topical tags")
    score: Optional[int] = Field(default=None, description="User rating: 1 for like, 0 for dislike")

class UserProfile(BaseModel):
    """The evolving model of user interests."""
    interests: List[str] = Field(description="List of core topics the user is interested in")
    refined_bio: str = Field(
        description="A detailed summary of user preferences based on feedback history",
        default="New user with a clean slate."
    )
    history: List[Article] = Field(default_factory=list, description="History of articles and ratings")
