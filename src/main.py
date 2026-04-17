from src.database import init_db
from src.orchestrator import NewsOrchestrator

def main():
    init_db()
    orchestrator = NewsOrchestrator()
    print("--- Personalized News Curator ---")
    
    # Profile Initialization Logic
    if orchestrator.load_existing_profile():
        print(f"\n[System] Found profile: {', '.join(orchestrator.profile.interests)}")
        resume = input("Would you like to continue with this profile? (y/n): ").lower()
        if resume != 'y':
            orchestrator.profile = None

    if not orchestrator.profile:
        topics_str = input("Enter 3 topics you are interested in (comma separated): ")
        initial_topics = [t.strip() for t in topics_str.split(",") if t.strip()]
        orchestrator.create_new_profile(initial_topics)

    print("\n[System] Curating your first batch of news...")
    orchestrator.seed_queue()

    while True:
        current = orchestrator.get_next_article()
        
        if not current:
            print("\n[System] No articles in queue.")
            choice = input("Enter a topic to search or 'exit': ").strip()
            if choice.lower() == 'exit': break
            orchestrator.fetch_and_enqueue(choice)
            continue

        # UI: Display Article
        print(f"\n>>> ARTICLE: {current.title}")
        print(f"Summary: {current.summary}")
        print(f"Tags: {', '.join(current.tags)}")
        print(f"Source: {current.url}")

        # UI: Feedback Loop
        feedback = ""
        while feedback not in ['y', 'n']:
            feedback = input("Did you like this article? (y/n): ").lower()
        
        print("[System] Updating your interest model...")
        orchestrator.process_feedback(current, liked=(feedback == 'y'))
        print(f"New Insight: {orchestrator.profile.refined_bio}")

        # UI: Navigation
        print(f"\nQueue size: {len(orchestrator.article_queue)}")
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