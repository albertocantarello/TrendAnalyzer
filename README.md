# R-TrendAnalyzer: Legali, Fisco, Carriera

Questa è una **Dashboard Serverless automatica** che estrae ogni settimana le domande più calde dai Subreddit italiani filtrando il rumore grazie all'Intelligenza Artificiale (Google Gemini).

## 🚀 Come Configurare il Progetto Messo a Prova di Principiante

Ti basta UNA sola "chiave magica". Passiamo Subito all'Azione:

### 1. Carica il Codice su GitHub
(Fatto insieme ad Antigravity)

### 2. Inserisci la chiave dell'IA su GitHub
L'unica chiave necessaria è quella di Google Gemini.
Nel tuo nuovo repository su GitHub, vai in alto su **Settings > Secrets and variables > Actions** e clicca sul pulsante verde **New repository secret**.

- Come nome metti esattamente: `GEMINI_API_KEY`
- Come valore metti la lunga stringa di Google (quella che inizia con AIza...).
- Inserisci *solo* questa chiave, non serve altro!

### 3. Attiva la tua Dashboard online (GitHub Pages)
Ora accendiamo il sito gratuito:
1. Sempre nel tuo repository, dal menu a sinistra vai su **Pages** (sotto Settings).
2. Sotto "Build and deployment", come "Source" scegli **Deploy from a branch**.
3. Sotto "Branch", seleziona **main** e clicca **Save**.
4. Attendi un paio di minuti, aggiorna la pagina, e vedrai in alto l'URL del tuo sito!

### 4. Fai il primo avvio manuale (Per caricare i dati veri)
1. Vai nel tab **Actions** (nella barra in alto del repository).
2. A sinistra clicca su "Weekly Trend Analysis".
3. A destra clicca sul bottoncino grigio **"Run workflow"** e avvialo.
4. Quando ha finito (1-2 minuti e compare la spunta verde), la tua web-app è popolata e lo script è programmato per ripetersi da solo ogni lunedì!
