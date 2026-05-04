import requests

def get_series_info(dns, user, password, series_id):
    """Consulta melhorada para contar temporadas com mais precisão."""
    if not series_id:
        return "ID Ausente"
        
    url = f"{dns}/player_api.php?username={user}&password={password}&action=get_series_info&series_id={series_id}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            
            # Tenta pegar da lista de temporadas
            seasons = data.get('seasons', [])
            if isinstance(seasons, list) and len(seasons) > 0:
                return f"{len(seasons)} Temp."
            
            # Caso o servidor retorne de um jeito diferente (como um dicionário)
            if isinstance(seasons, dict) and len(seasons) > 0:
                return f"{len(seasons)} Temp."
                
            # Se não achou 'seasons', tenta contar os episódios agrupados (fallback)
            episodes = data.get('episodes', {})
            if episodes:
                return f"{len(episodes)} Temp."
                
    except:
        return "Erro API"
    return "1 Temp." # Padrão caso encontre a série mas não a contagem

def search_content_in_dns(dns, user, password, query, mode, timeout=10):
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): dns = 'http://' + dns
    
    action = "get_vod_streams" if mode == "Filmes" else "get_series"
    url = f"{dns}/player_api.php?username={user}&password={password}&action={action}"
    
    try:
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
                            # Tenta pegar o ID da série (pode ser series_id ou id)
                            s_id = item.get('series_id') or item.get('id')
                            info = get_series_info(dns, user, password, s_id)
                            matches.append(f"📺 {name} ({info})")
                
                if matches:
                    return {"dns": dns, "encontrados": matches[:10], "total": len(matches)}
    except:
        pass
    return None

# O restante do código (run_sequential_search) permanece igual
