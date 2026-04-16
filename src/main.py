import json
import os
from datetime import datetime
from reddit_scraper import RedditScraper
from ai_processor import AIProcessor

def main():
    print("=== Inizio analisi dei trend di Reddit ===")
    
    # 1. Scraping
    try:
        scraper = RedditScraper()
        posts = scraper.get_weekly_posts()
        print(f"Estratti {len(posts)} post candidati.")
    except Exception as e:
        print(f"ERRORE RedditScraper: {e}")
        return

    if not posts:
        print("Nessun post trovato.")
        return

    # 1b. Salva i post raw per trasparenza e debug
    os.makedirs("data", exist_ok=True)
    raw_file = os.path.join("data", "raw_posts.json")
    raw_data = {
        "scraped_at": datetime.now().isoformat(),
        "total_posts": len(posts),
        "posts": posts
    }
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)
    print(f"Post raw salvati in {raw_file} per verifica.")

    # Mostra distribuzione per subreddit
    sub_counts = {}
    for p in posts:
        sub = p.get('subreddit', 'unknown')
        sub_counts[sub] = sub_counts.get(sub, 0) + 1
    print("Distribuzione post per subreddit:")
    for sub, count in sorted(sub_counts.items(), key=lambda x: -x[1]):
        print(f"  r/{sub}: {count} post")

    # 2. IA Processing
    try:
        processor = AIProcessor()
        
        from collections import defaultdict
        grouped_posts = defaultdict(list)
        for p in posts:
            grouped_posts[p.get('subreddit', 'unknown')].append(p)
            
        trends = []
        for sub, sub_posts in grouped_posts.items():
            if sub == 'unknown':
                continue
            print(f"Elaborazione IA per r/{sub} ({len(sub_posts)} post)...")
            sub_trends = processor.process_posts(sub_posts, sub_name=sub)
            trends.extend(sub_trends)
            
        print(f"Claude ha trovato un totale di {len(trends)} trend distinti.")
    except Exception as e:
        print(f"ERRORE AIProcessor: {e}")
        return

    # 3. Output
    os.makedirs("../data", exist_ok=True)
    out_data = {
        "last_update": datetime.now().isoformat(),
        "trends": trends
    }
    
    # Il file si aspetta di essere in /data, creiamolo
    # Assumiamo che main.py sia eseguito da root o da src
    base_path = "data"
    if not os.path.exists(base_path) and os.path.basename(os.getcwd()) == "src":
        base_path = "../data"
        
    os.makedirs(base_path, exist_ok=True)
    out_file = os.path.join(base_path, "trends.json")
    
    # Crea un mock-up finto nel caso in cui le liste siano vuote, giusto per il frontend
    if not trends:
        out_data["trends"] = [
            {
                "trend_name": "Regime Forfettario 2024",
                "frequency": "Alta",
                "post_count": 0,
                "main_question": "Quali sono i limiti reali di spesa per il forfettario?",
                "content_idea": "Video Youtube: I 3 miti da sfatare sul Regime Forfettario.",
                "subreddits": ["r/commercialisti"]
            }
        ]
        out_data["last_update"] = "Dato dimostrativo (Mancano API Keys)"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
        
    print(f"Salvataggio completato in {out_file}.")
    print("=== Procedura terminata ===")

if __name__ == "__main__":
    main()
