import os
import time
import http.server
import socketserver
import threading
import smtplib
from email.message import EmailMessage
from playwright.sync_api import sync_playwright

PORT = 8000
SERVER_DIR = "."  # We will navigate to the root directory where index.html exists

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Suppress logs for cleaner output

def start_server():
    os.chdir("..") # Assumendo che venga lanciato da src/, andiamo nella root
    handler = QuietHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.daemon = True
    thread.start()
    return httpd

def generate_pdf(output_path):
    print("Avvio browser invisibile per generazione PDF...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Imposta la dimensione per la stampa
        page.set_viewport_size({"width": 1280, "height": 1024})
        
        print(f"Navigazione verso http://localhost:{PORT}/index.html")
        page.goto(f"http://localhost:{PORT}/index.html", wait_until="networkidle")
        
        # Attende che il JS carichi e mostri i trend (il loading ring scompare)
        print("In attesa del rendering della pagina...")
        page.wait_for_selector("#trends-container:not(.hidden)", timeout=15000)
        
        # Una piccola pausa bonus per permettere alle animazioni CSS Tailwind di assestarsi (fade-in)
        time.sleep(2)

        # Rimuoviamo il bottone "invia email" o elementi interattivi se necessario
        # (al momento non ne abbiamo, è una dashboard)

        print("Generazione PDF in corso...")
        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,  # Preserva colori scuri Tailwind
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
        )
        browser.close()
        print(f"PDF salvato con successo in {output_path}")

def send_email(pdf_path, smtp_user, smtp_pass, recipients):
    print("Preparazione invio email...")
    
    msg = EmailMessage()
    msg['Subject'] = 'TrendAnalyzer: Report Settimanale Reddit'
    msg['From'] = smtp_user
    msg['To'] = ", ".join(recipients)
    
    body = (
        "Ciao!\n\n"
        "In allegato trovi il nuovo report settimanale in formato PDF "
        "con le domande ed i trend più caldi su Reddit.\n\n"
        "Buona lettura e buona creazione di contenuti!\n"
        "--\n"
        "Generato automaticamente da R-TrendAnalyzer"
    )
    msg.set_content(body)
    
    # Allegare il PDF
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))
    
    try:
        # Usa server Gmail di default (è il più comune, in caso l'utente potrà cambiarlo)
        # Se Outlook usare: smtp-mail.outlook.com, port 587
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        print(f"Email inviata con successo ai {len(recipients)} destinatari configurati!")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")

if __name__ == "__main__":
    # Inizializza server web
    # Se viene chiamato da root, andiamo in src e avviamo.
    if os.path.basename(os.getcwd()) != "src":
        os.chdir("src")
        
    http_server = start_server()
    pdf_filename = "../data/trend_report_settimanale.pdf"
    
    try:
        generate_pdf(pdf_filename)
        
        # Estrai le variabili segrete configurate in Github Actions
        smtp_user = os.environ.get("SMTP_USER", "")
        smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        recipients_env = os.environ.get("EMAIL_RECIPIENTS", "")
        
        # Split e ripulitura lista destinatari (es. d1@m.it, d2@m.it )
        recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]

        if smtp_user and smtp_pass and recipients:
            send_email(pdf_filename, smtp_user, smtp_pass, recipients)
        else:
            print("Invio email ignorato: variabili d'ambiente (SMTP_USER, SMTP_PASSWORD, EMAIL_RECIPIENTS) mancanti o vuote.")
            
    finally:
        http_server.shutdown()
        http_server.server_close()
