import requests
from concurrent.futures import ThreadPoolExecutor

def validar_conexao_m3u(dns, user, password, timeout=7):
    """
    Tenta validar o acesso ao servidor montando a URL de teste.
    """
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): 
        dns = 'http://' + dns
    
    # Montamos a URL conforme o exemplo que você passou
    # Usamos o endpoint player_api.php por ser mais leve para teste em massa que o get.php
    url_teste = f"{dns}/player_api.php?username={user}&password={password}"
    
    try:
        response = requests.get(url_teste, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            # Verifica se as credenciais digitadas são válidas para este DNS
            if data.get("user_info", {}).get("auth") == 1:
                return {
                    "dns": dns,
                    "m3u_completo": f"{dns}/get.php?username={user}&password={password}&type=m3u_plus&output=mpegts",
                    "status": "✅ Funcional",
                    "expira": data["user_info"].get("exp_date", "Sem data")
                }
    except:
        pass
    return None

def iniciar_varredura(lista_dns, user, password, threads, timeout):
    resultados = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        tarefas = [executor.submit(validar_conexao_m3u, d, user, password, timeout) for d in lista_dns]
        for t in tarefas:
            res = t.result()
            if res:
                resultados.append(res)
    return resultados
