import requests

def get_series_info(dns, user, password, series_id):
    """Consulta para contar temporadas."""
    if not series_id:
        return "1 Temp."
        
    url = f"{dns}/player_api.php?username={user}&password={password}&action=get_series_info&series_id={series_id}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Tenta contar temporadas em 'seasons' ou 'episodes'
            seasons = data.get('seasons', [])
            if seasons:
                return f"{len(seasons)} Temp."
            
            episodes = data.get('episodes', {})
            if episodes:
                return f"{len(episodes)} Temp."
    except:
        pass
    return "1 Temp."

def search_content_in_dns(dns, user, password, query, mode, timeout=10):
    """Busca individual por DNS."""
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): 
        dns = 'http://' + dns
    
    action = "get_vod_streams" if mode == "Filmes" else "get_series"
    url = f"{dns}/player_api.php?username={user}&password={password}&action={action}"
    
    try:
        # Timeout curto para não travar o app
        with requests.get(url, timeout=timeout, stream=True) as r:
            if r.status_code == 200:
                catalog = r.json()
                query_lower = query.lower()
                matches = []

                for item in catalog:
                    name = str(item.get('name', ''))
                    if query_lower in name.lower():
                        if mode == "Filmes":
                            matches.append(f"🎬 {name}")
                        else:
                            s_id = item.get('series_id') or item.get('id')
                            info = get_series_info(dns, user, password, s_id)
                            matches.append(f"📺 {name} ({info})")
                
                if matches:
                    return {"dns": dns, "encontrados": matches[:10], "total": len(matches)}
    except:
        pass
    return None

def run_sequential_search(dns_list, user, password, query, mode, progress_bar, status_text):
    """Loop sequencial para evitar estouro de memória."""
    results = []
    total = len(dns_list)
    for i, dns in enumerate(dns_list):
        status_text.text(f"🔎 Buscando {mode} em {i+1}/{total}: {dns}")
        progress_bar.progress((i + 1) / total)
        res = search_content_in_dns(dns, user, password, query, mode)
        if res:
            results.append(res)
    return results
