import requests

def search_content_in_dns(dns, user, password, query, mode, timeout=10):
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): 
        dns = 'http://' + dns
    
    # Define a ação com base na escolha: Filmes (vod) ou Séries (series)
    action = "get_vod_streams" if mode == "Filmes" else "get_series"
    url = f"{dns}/player_api.php?username={user}&password={password}&action={action}"
    
    try:
        with requests.get(url, timeout=timeout, stream=True) as r:
            if r.status_code == 200:
                catalog = r.json()
                query_lower = query.lower()
                matches = []

                for item in catalog:
                    name = item.get('name', '')
                    if query_lower in str(name).lower():
                        if mode == "Filmes":
                            matches.append(f"🎬 {name}")
                        else:
                            # Para séries, buscamos informações extras de temporadas
                            series_id = item.get('series_id')
                            info_serie = get_series_info(dns, user, password, series_id)
                            matches.append(f"📺 {name} ({info_serie})")
                
                if matches:
                    return {"dns": dns, "encontrados": matches[:10], "total": len(matches)}
    except:
        pass
    return None

def get_series_info(dns, user, password, series_id):
    """Consulta rápida para contar temporadas de uma série específica."""
    url = f"{dns}/player_api.php?username={user}&password={password}&action=get_series_info&series_id={series_id}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            # Conta quantas temporadas existem na lista 'seasons'
            seasons = data.get('seasons', [])
            qtd = len(seasons)
            return f"{qtd} Temp." if qtd > 0 else "Info Indisp."
    except:
        return "Erro ao carregar temporadas"
    return "N/A"

def run_sequential_search(dns_list, user, password, query, mode, progress_bar, status_text):
    results = []
    total_dns = len(dns_list)
    for i, dns in enumerate(dns_list):
        status_text.text(f"🔎 Buscando {mode} em {i+1}/{total_dns}: {dns}")
        progress_bar.progress((i + 1) / total_dns)
        res = search_content_in_dns(dns, user, password, query, mode)
        if res:
            results.append(res)
    return results
