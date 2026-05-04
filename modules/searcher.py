import requests
from concurrent.futures import ThreadPoolExecutor

def buscar_nos_servidores(dns, user, password, termo_busca):
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): dns = 'http://' + dns
    
    # Endpoint para buscar a lista de filmes (VOD)
    url_busca = f"{dns}/player_api.php?username={user}&password={password}&action=get_vod_streams"
    
    try:
        r = requests.get(url_busca, timeout=10)
        if r.status_code == 200:
            filmes = r.json()
            # Filtra os filmes que contenham o termo de busca no nome
            encontrados = [f['name'] for f in filmes if termo_busca.lower() in f['name'].lower()]
            
            if encontrados:
                return {
                    "dns": dns,
                    "encontrados": encontrados[:5], # Retorna os 5 primeiros resultados
                    "total": len(encontrados)
                }
    except:
        pass
    return None
