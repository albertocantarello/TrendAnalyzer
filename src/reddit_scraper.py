import feedparser
import time

class RedditScraper:
    def __init__(self):
        # Con il metodo RSS non servono più API Keys e password!
        pass

    def get_weekly_posts(self):
        target_subs = ['Avvocati', 'commercialisti', 'ItaliaPersonalFinance', 'ItaliaCareerAdvice']
        general_subs = ['italy', 'Italia']
        keywords = ['commercialista', 'avvocato', 'tasse', 'licenziamento', 'legale', 'dimissioni']
        
        all_posts = []
        
        print("Scaricando dai subreddit specifici tramite RSS (Aggiramento Blocchi Reddit)...")
        for sub_name in target_subs:
            try:
                url = f"https://www.reddit.com/r/{sub_name}/top/.rss?t=week"
                feed = feedparser.parse(url)
                for entry in feed.entries[:30]:
                    all_posts.append({
                        "id": entry.get('id', ''),
                        "title": entry.get('title', ''),
                        "selftext": entry.get('summary', ''),
                        "url": entry.get('link', ''),
                        "subreddit": sub_name,
                        "source_type": "specific_sub"
                    })
                time.sleep(1) # Cortesia per non farsi bloccare
            except Exception as e:
                print(f"Errore leggendo r/{sub_name}: {e}")
                
        print("Scaricando dai subreddit generalisti...")
        for sub_name in general_subs:
            for kw in keywords:
                try:
                    url = f"https://www.reddit.com/r/{sub_name}/search.rss?q={kw}&restrict_sr=on&t=week"
                    feed = feedparser.parse(url)
                    for entry in feed.entries[:10]:
                        if not any(p['id'] == entry.get('id') for p in all_posts):
                            all_posts.append({
                                "id": entry.get('id', ''),
                                "title": entry.get('title', ''),
                                "selftext": entry.get('summary', ''),
                                "url": entry.get('link', ''),
                                "subreddit": sub_name,
                                "source_type": "keyword_search"
                            })
                    time.sleep(1)
                except Exception as e:
                    print(f"Errore cercando in r/{sub_name}: {e}")
                        
        return all_posts
