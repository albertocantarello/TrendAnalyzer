import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

class AIProcessor:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY mancante!")
        self.client = anthropic.Anthropic(api_key=api_key)

    def process_posts(self, posts, sub_name=""):
        if not posts:
            return []

        text_to_analyze = ""
        for i, p in enumerate(posts):
            text = (p.get('selftext') or "").strip()
            text_to_analyze += "ID: " + str(p['id']) + " | Titolo: " + p['title'] + "\nTesto: " + text[:800] + "\n---\n"

        target_audience = "professionisti italiani"
        if sub_name == "commercialisti":
            target_audience = "Commercialisti e Fiscalisti"
        elif sub_name.lower() == "avvocati":
            target_audience = "Avvocati e Legali"
        elif sub_name == "consulentidellavoro":
            target_audience = "Consulenti del lavoro e HR"

        prompt = f"""Sei un assistente esperto in analisi dei trend per {target_audience}.
Di seguito trovi {len(posts)} post estratti dal subreddit r/{sub_name} questa settimana.

REGOLE FONDAMENTALI:
1. NON raggruppare troppo! Se due argomenti sono anche solo leggermente diversi, tienili separati.
2. Filtra SOLO lo spam puro (meme, post senza contenuto). Se un post ha una domanda reale, anche banale, INCLUDILO.
3. Identifica 5-8 trend distinti e rilevanti per questa categoria professionale derivanti dai post indicati.
4. Se un argomento appare in un solo post ma e' una domanda professionale valida, includilo con frequenza "Bassa".

Per ogni trend identificato, fornisci:
- "trend_name": Titolo del trend (breve e d'impatto).
- "frequency": "Alta" (5+ post), "Media" (2-4 post), "Bassa" (1 post).
- "post_count": Numero esatto di post che trattano questo tema.
- "main_question": La vera domanda professionale estratta dai post.
- "content_idea": Un'idea per un contenuto (video, post, reel) su questo tema.
- "subreddits": Lista dei subreddit da cui provengono i post (in questo caso inserisci ["r/{sub_name}"]).

Restituisci l'output ESCLUSIVAMENTE in formato JSON valido come Array di oggetti, e nessun altro testo:
[
  {{
    "trend_name": "...",
    "frequency": "...",
    "post_count": 0,
    "main_question": "...",
    "content_idea": "...",
    "subreddits": ["r/{sub_name}"]
  }}
]

Ecco i {len(posts)} post da analizzare:
{text_to_analyze}"""

        print(f"Invio {len(posts)} post (r/{sub_name}) a Claude Sonnet per analisi...")
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            try:
                return json.loads(text.strip(), strict=False)
            except Exception as je:
                print("Errore decodifica JSON (" + str(je) + ") per " + sub_name)
                os.makedirs("data", exist_ok=True)
                with open(f"data/claude_error_output_{sub_name}.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"Salvato l'output grezzo in data/claude_error_output_{sub_name}.txt per debug.")
                return []
        except Exception as e:
            print(f"Errore API o elaborazione IA per {sub_name}: " + str(e))
            return []
