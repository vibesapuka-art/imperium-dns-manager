import requests

def search_content_in_dns(dns, user, password, query, timeout=10):
    """
    Busca um título em um servidor específico de forma isolada para poupar memória.
    """
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): 
        dns = 'http://' + dns
    
    # Endpoint de Filmes (VOD) - Ação para listar filmes
    url = f"{dns}/player_api.php?username={user}&password={password}&action=get_vod_streams"
    
    try:
        # stream=True ajuda a não carregar o peso do arquivo na memória de uma vez só
        with requests.get(url, timeout=timeout, stream=True) as r:
            if r.status_code == 200:
                catalog = r.json()
                query_lower = query.lower()
                
                # Filtra os itens que contêm o termo buscado no nome
                matches = [item.get('name') for item in catalog if query_lower in str(item.get('name', '')).lower()]
                
                if matches:
                    return {
                        "dns": dns,
                        "encontrados": matches[:10], # Retorna os 10 primeiros nomes
                        "total": len(matches)
                    }
    except Exception:
        # Pula silenciosamente se o servidor estiver lento ou der erro no JSON
        pass
    return None

def run_sequential_search(dns_list, user, password, query, progress_bar, status_text):
    """
    Executa a busca percorrendo a lista um por um para evitar crash de memória.
    """
    results = []
    total_dns = len(dns_list)
    
    for i, dns in enumerate(dns_list):
        # Atualiza o progresso na tela do Streamlit
        status_text.text(f"🔎 Buscando no servidor {i+1} de {total_dns}: {dns}")
        progress_bar.progress((i + 1) / total_dns)
        
        res = search_content_in_dns(dns, user, password, query)
        if res:
            results.append(res)
            
    return results
