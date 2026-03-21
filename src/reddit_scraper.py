import feedparser
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime


class RedditScraper:
    def __init__(self):
        # Con il metodo RSS non servono più API Keys e password!
        self.cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    def _parse_entry_date(self, entry):
        """Estrae la data di pubblicazione da un entry RSS di Reddit."""
        # Reddit RSS usa il campo 'published' in formato ISO/RFC
        date_str = entry.get('published', entry.get('updated', ''))
        if not date_str:
            return None
        try:
            # feedparser converte già in struct_time, usiamo il campo parsed
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                from calendar import timegm
                return datetime.fromtimestamp(timegm(entry.published_parsed), tz=timezone.utc)
            # Fallback: parse manuale
            return parsedate_to_datetime(date_str)
        except Exception:
            return None

    def _fetch_sub_new(self, sub_name, all_posts):
        """Scarica TUTTI i post degli ultimi 7 giorni da un subreddit usando /new/ con paginazione."""
        after = None
        page = 0
        max_pages = 10  # Limite di sicurezza per evitare loop infiniti

        while page < max_pages:
            url = f"https://www.reddit.com/r/{sub_name}/new/.rss"
            if after:
                url += f"?after={after}"

            try:
                feed = feedparser.parse(url)
            except Exception as e:
                print(f"  Errore leggendo r/{sub_name} (pagina {page}): {e}")
                break

            if not feed.entries:
                break

            found_old = False
            last_id = None

            for entry in feed.entries:
                post_date = self._parse_entry_date(entry)

                # Se il post è più vecchio di 7 giorni, fermiamo la paginazione
                if post_date and post_date < self.cutoff:
                    found_old = True
                    break

                full_id = entry.get('id', '')
                # Reddit RSS restituisce ID come URL completo, es:
                # https://www.reddit.com/r/commercialisti/new/t3_1rxlxwm
                # Estraiamo il t3_xxx per la paginazione
                short_id = full_id.split('/')[-1] if '/' in full_id else full_id

                # Evita duplicati
                if any(p['id'] == short_id for p in all_posts):
                    continue

                all_posts.append({
                    "id": short_id,
                    "title": entry.get('title', ''),
                    "selftext": entry.get('summary', ''),
                    "url": entry.get('link', ''),
                    "subreddit": sub_name,
                    "source_type": "specific_sub",
                    "published": post_date.isoformat() if post_date else ""
                })
                last_id = short_id

            if found_old or not last_id:
                break

            after = last_id
            page += 1
            time.sleep(2)  # Rate limiting per non farsi bloccare

        return all_posts

    def get_weekly_posts(self):
        target_subs = ['consulentidellavoro', 'Avvocati', 'commercialisti']

        all_posts = []

        print("Scaricando dai subreddit specifici tramite RSS (/new/ con paginazione)...")
        for sub_name in target_subs:
            count_before = len(all_posts)
            self._fetch_sub_new(sub_name, all_posts)
            count_after = len(all_posts)
            print(f"  r/{sub_name}: {count_after - count_before} post degli ultimi 7 giorni")
            time.sleep(1)

        print(f"Totale post raccolti: {len(all_posts)}")
        return all_posts
