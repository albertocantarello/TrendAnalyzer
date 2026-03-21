document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});

async function fetchData() {
    const container = document.getElementById('trends-container');
    const loadingRing = document.getElementById('loading');
    const updateTime = document.getElementById('update-time');
    
    try {
        // Appende un timestamp fittizio per baipassare la cache del browser su GitHub Pages
        const response = await fetch('data/trends.json?t=' + new Date().getTime());
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Nasconde il loading state
        loadingRing.classList.add('hidden');
        container.classList.remove('hidden');
        
        // Imposta la data di ultimo aggiornamento
        if(data.last_update.includes("Dato dimostrativo")) {
             updateTime.innerHTML = `<span class="text-yellow-400"><i class="fas fa-exclamation-circle mr-1"></i> Dati Demo (In attesa del primo avvio)</span>`;
        } else {
             const d = new Date(data.last_update);
             // Formattazione data italiana carina
             const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute:'2-digit' };
             updateTime.textContent = d.toLocaleDateString('it-IT', options);
        }
        
        renderTrends(data.trends, container);
    } catch (error) {
        loadingRing.classList.add('hidden');
        container.classList.remove('hidden');
        
        // Se c'è un errore (es. JSON non trovato perché è il primo avvio e GitHub non l'ha ancora generato)
        container.innerHTML = `
            <div class="col-span-1 md:col-span-2 lg:col-span-3 flex flex-col items-center justify-center text-center p-12 glass-card rounded-2xl border-yellow-500/20">
                <div class="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
                    <i class="fas fa-robot text-3xl text-yellow-500"></i>
                </div>
                <h3 class="text-xl font-bold text-white mb-2">In attesa dei dati...</h3>
                <p class="text-slate-400 max-w-md">I trend settimanali non sono ancora stati generati. Quando le GitHub Actions avvieranno lo script Python, i dati appariranno qui magicamente.</p>
            </div>`;
        console.error("Fetch Data Error: ", error);
    }
}

function renderTrends(trends, container) {
    container.innerHTML = '';

    if(!trends || trends.length === 0) {
        container.innerHTML = '<div class="col-span-full text-center text-slate-400 p-8 glass-card rounded-xl">Nessuna domanda rilevante trovata questa settimana.</div>';
        return;
    }

    trends.forEach(function(trend, index) {
        var freqColor = "bg-slate-700/50 text-slate-300 border-slate-600";
        var icon = "fa-fire";

        if(trend.frequency.toLowerCase() === 'alta') {
            freqColor = "bg-red-500/10 text-red-400 border-red-500/20";
            icon = "fa-fire-flame-curved";
        } else if(trend.frequency.toLowerCase() === 'media') {
            freqColor = "bg-orange-500/10 text-orange-400 border-orange-500/20";
            icon = "fa-chart-simple";
        } else if(trend.frequency.toLowerCase() === 'bassa') {
            freqColor = "bg-blue-500/10 text-blue-400 border-blue-500/20";
            icon = "fa-seedling";
        }

        var card = document.createElement('div');
        card.className = "glass-card rounded-2xl p-6 flex flex-col h-full animate-fade-in-up";
        card.style.animationDelay = (index * 0.1) + "s";

        // Costruisci la riga dei subreddit se disponibili
        var subredditHtml = '';
        if (trend.subreddits && trend.subreddits.length > 0) {
            subredditHtml = '<div class="flex flex-wrap gap-1.5 mt-3">';
            trend.subreddits.forEach(function(sub) {
                subredditHtml += '<span class="px-2 py-0.5 rounded-full text-[10px] font-medium bg-purple-500/10 text-purple-400 border border-purple-500/20">' + sub + '</span>';
            });
            subredditHtml += '</div>';
        }

        // Badge conteggio post
        var postCountHtml = '';
        if (trend.post_count) {
            postCountHtml = '<span class="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-slate-700/50 text-slate-400 border border-slate-600/50">' +
                '<i class="fa-solid fa-message mr-1"></i>' + trend.post_count + ' post</span>';
        }

        card.innerHTML =
            '<div class="flex justify-between items-start mb-5 gap-3">' +
                '<h3 class="text-lg font-bold text-white transition-colors leading-snug">' + trend.trend_name + '</h3>' +
                '<div class="flex items-center gap-2 shrink-0">' +
                    postCountHtml +
                    '<span class="px-2.5 py-1 rounded-md text-xs font-semibold border flex items-center ' + freqColor + '">' +
                        '<i class="fa-solid ' + icon + ' mr-1.5 opacity-80"></i>' + trend.frequency +
                    '</span>' +
                '</div>' +
            '</div>' +
            '<div class="mb-5 flex-grow group">' +
                '<p class="text-xs text-slate-500 mb-2 uppercase tracking-widest font-semibold ml-1">Domanda Originale Rielaborata</p>' +
                '<div class="relative">' +
                    '<i class="fa-solid fa-quote-left absolute -top-2 -left-2 text-3xl text-slate-700/30 -z-10 group-hover:text-accent/20 transition-colors"></i>' +
                    '<p class="text-slate-200 font-medium italic border-l-2 border-accent/70 pl-3 py-1 relative z-10">"' + trend.main_question + '"</p>' +
                '</div>' +
                subredditHtml +
            '</div>' +
            '<div class="mt-auto pt-4 border-t border-slate-700/60 bg-slate-800/30 -mx-6 -mb-6 px-6 pb-6 rounded-b-2xl">' +
                '<p class="text-[11px] font-bold text-emerald-400 mb-1 uppercase tracking-widest flex items-center">' +
                    '<i class="fa-solid fa-wand-magic-sparkles mr-1.5 text-lg"></i> Spunto per Creator' +
                '</p>' +
                '<p class="text-slate-300 text-sm leading-relaxed">' + trend.content_idea + '</p>' +
            '</div>';

        container.appendChild(card);
    });
}
