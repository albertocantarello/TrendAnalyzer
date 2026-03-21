import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AIProcessor:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY mancante!")
        self.client = genai.Client(api_key=api_key)

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

        print("Invio dati a Gemini...")
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text.strip())
        except Exception as e:
            print("Errore durante l'elaborazione IA: " + str(e))
            try:
                print("Risposta grezza IA: " + str(response.text))
            except:
                pass
            return []
