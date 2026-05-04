import requests
from concurrent.futures import ThreadPoolExecutor

def search_content_in_dns(dns, user, password, query, timeout=12):
    """
    Busca um termo específico no catálogo de filmes (VOD) do servidor.
    """
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): 
        dns = 'http://' + dns
    
    # Endpoint para pegar a lista de Streams de VOD
    url = f"{dns}/player_api.php?username={user}&password={password}&action=get_vod_streams"
    
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            catalog = response.json()
            # Filtra itens que contenham o termo buscado (sem diferenciar maiúsculas/minúsculas)
            matches = [item['name'] for item in catalog if query.lower() in item['name'].lower()]
            
            if matches:
                return {
                    "dns": dns,
                    "encontrados": matches[:10], # Mostra os 10 primeiros resultados
                    "total": len(matches)
                }
    except:
        pass
    return None

def run_global_search(dns_list, user, password, query, threads):
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(search_content_in_dns, d, user, password, query) for d in dns_list]
        for f in futures:
            res = f.result()
            if res:
                results.append(res)
    return results
