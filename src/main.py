import sys
from src.models import UserProfile, Article
from src.agent import NewsAgent
from src.database import init_db, save_profile, load_profile

def main():
    init_db()
    agent = NewsAgent()
    print("--- Personalized News Curator ---")
    
    # Load existing profile or start new
    profile = load_profile()
    if profile:
        print(f"\n[System] Found existing profile for: {', '.join(profile.interests)}")
        resume = input("Would you like to continue with this profile? (y/n): ").lower()
        if resume != 'y':
            profile = None

    if not profile:
        # Initial setup
        topics_str = input("Enter 3 topics you are interested in (comma separated): ")
        initial_topics = [t.strip() for t in topics_str.split(",") if t.strip()]
        profile = UserProfile(interests=initial_topics)
        save_profile(profile)

    article_queue = []
    # Initial seeding
    print("\n[System] Curating your first batch of news...")
    seed_topics = profile.interests[:3]
    for topic in seed_topics:
        article = agent.get_next_article(profile, topic)
        article_queue.append(article)

    while True:
        if not article_queue:
            print("\n[System] Queue is empty.")
            new_topic = input("Enter a topic to explore or 'exit': ")
            if new_topic.lower() == 'exit': break
            article_queue.append(agent.get_next_article(profile, new_topic))
            continue

        # Show article
        current = article_queue.pop(0)
        print(f"\n>>> ARTICLE: {current.title}")
        print(f"Summary: {current.summary}")
        print(f"Tags: {', '.join(current.tags)}")
        print(f"Source: {current.url}")

        # Get feedback
        feedback = ""
        while feedback not in ['y', 'n']:
            feedback = input("Did you like this article? (y/n): ").lower()
        
        current.score = 1 if feedback == 'y' else 0
        profile.history.append(current)

        # Update Bio (The Agentic Feedback Loop)
        print("[System] Updating your interest model...")
        profile.refined_bio = agent.update_profile(profile, current)
        save_profile(profile)
        print(f"New Insight: {profile.refined_bio}")

        # Fetch a new article based on interests to keep the queue going
        # We alternate between the original topics and the refined bio
        next_topic = profile.interests[len(profile.history) % len(profile.interests)]
        print(f"[System] Adding a new article about '{next_topic}' to the queue...")
        article_queue.append(agent.get_next_article(profile, next_topic))

        # Decision point
        print(f"\nQueue size: {len(article_queue)}")
        choice = input("Press Enter for next article, type a NEW topic to explore, or 'exit': ").strip()
        
        if choice.lower() == 'exit':
            print("Goodbye!")
            break
        elif choice:
            # User wants a specific new topic
            print(f"[System] Adding '{choice}' to your interests...")
            profile.interests.append(choice)
            new_art = agent.get_next_article(profile, choice)
            # Jump it to the front of the queue
            article_queue.insert(0, new_art)

if __name__ == "__main__":
    main()