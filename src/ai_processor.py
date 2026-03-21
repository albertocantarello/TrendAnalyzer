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

    def process_posts(self, posts):
        if not posts:
            return []

        text_to_analyze = ""
        for i, p in enumerate(posts):
            text = (p.get('selftext') or "").strip()
            text_to_analyze += "ID: " + str(p['id']) + " | Subreddit: r/" + p['subreddit'] + " | Titolo: " + p['title'] + "\nTesto: " + text[:800] + "\n---\n"

        prompt = """Sei un assistente esperto in analisi dei trend per professionisti italiani (Commercialisti, Avvocati, Consulenti del lavoro).
Di seguito trovi una lista di post estratti da Reddit questa settimana.

Il tuo compito e':
1. Filtrare il rumore: ignora post inutili senza una vera domanda tecnica/professionale.
2. Estrarre la problematica "core" da ogni post.
3. Raggruppare i problemi simili in MACRO-TREND.

Per ogni Macro-Trend identificato, fornisci:
- "trend_name": Il titolo del trend (breve e d'impatto).
- "frequency": "Alta", "Media" o "Bassa" in base al volume.
- "main_question": La vera domanda professionale estratta dai post confusi.
- "content_idea": Un'idea geniale per un video o un post su questo tema.

Restituisci l'output ESCLUSIVAMENTE in formato JSON valido come Array di oggetti, e nessun altro testo:
[
  {
    "trend_name": "...",
    "frequency": "...",
    "main_question": "...",
    "content_idea": "..."
  }
]

Ecco i post da analizzare:
""" + text_to_analyze

        print("Invio dati a Claude Sonnet...")
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            text = response.content[0].text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())
        except Exception as e:
            print("Errore durante l'elaborazione IA: " + str(e))
            return []
