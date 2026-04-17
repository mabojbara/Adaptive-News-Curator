from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.models import Article, UserProfile
from src.tools import get_search_tool, format_search_results

class NewsAgent:
    def __init__(self):
        # Using GPT-4o for better reasoning on reranking and summarization
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.search_tool = get_search_tool()

    def _generate_search_query(self, profile: UserProfile, topic: str) -> str:
        """Generates a tailored search query based on user preferences."""
        prompt = ChatPromptTemplate.from_template(
            "Generate a specific search query for news about '{topic}'. "
            "Consider the user's background: {bio}. "
            "Return only the search query string."
        )
        chain = prompt | self.llm
        response = chain.invoke({"topic": topic, "bio": profile.refined_bio})
        return response.content.strip()

    def get_next_article(self, profile: UserProfile, topic: str) -> Article:
        """Searches, reranks, and returns a single curated Article."""
        # 1. Generate optimized query
        query = self._generate_search_query(profile, topic)
        
        # 2. Search
        raw_results = self.search_tool.invoke(query)
        formatted_results = format_search_results(raw_results)

        # 3. Use LLM to pick the best article and structure it
        prompt = ChatPromptTemplate.from_template("""
            You are an expert news curator. Pick the single best article from the list below 
            that matches the user's interests.

            User Bio: {bio}
            Search Results:
            {results}

            Provide a summary and relevant tags.
        """)
        
        structured_llm = self.llm.with_structured_output(Article)
        chain = prompt | structured_llm
        
        return chain.invoke({"bio": profile.refined_bio, "results": formatted_results})

    def update_profile(self, profile: UserProfile, last_article: Article) -> str:
        """Updates the refined_bio based on the latest feedback."""
        prompt = ChatPromptTemplate.from_template("""
            Update the user's interest profile.
            Current Bio: {bio}
            Article Title: {title}
            User Feedback: {feedback} (1=Liked, 0=Disliked)

            Write a new, concise summary (1 paragraph) of the user's evolving interests. 
            Focus on what they specifically liked/disliked about this article.
        """)
        
        feedback_str = "Liked" if last_article.score == 1 else "Disliked"
        chain = prompt | self.llm
        response = chain.invoke({"bio": profile.refined_bio, "title": last_article.title, "feedback": feedback_str})
        return response.content.strip()