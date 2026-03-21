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

    # 2. IA Processing
    try:
        processor = AIProcessor()
        trends = processor.process_posts(posts)
        print(f"Gemini ha trovato {len(trends)} macro-trend validi.")
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
                "main_question": "Quali sono i limiti reali di spesa per il forfettario?",
                "content_idea": "Video Youtube: I 3 miti da sfatare sul Regime Forfettario."
            }
        ]
        out_data["last_update"] = "Dato dimostrativo (Mancano API Keys)"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)
        
    print(f"Salvataggio completato in {out_file}.")
    print("=== Procedura terminata ===")

if __name__ == "__main__":
    main()
