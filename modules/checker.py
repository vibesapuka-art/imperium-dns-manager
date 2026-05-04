import requests
from concurrent.futures import ThreadPoolExecutor

def validate_dns_credentials(dns, user, password, timeout=7):
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): 
        dns = 'http://' + dns
    
    # Testamos via Player API que é o método mais rápido e seguro para validar credenciais
    test_url = f"{dns}/player_api.php?username={user}&password={password}"
    
    try:
        # Usamos GET para verificar a resposta do servidor
        r = requests.get(test_url, timeout=timeout)
        
        if r.status_code == 200:
            data = r.json()
            # Se o servidor responder que a conta está ativa (auth=1)
            if data.get("user_info", {}).get("auth") == 1:
                status = data["user_info"].get("status")
                # Retornamos o DNS e o link m3u completo gerado
                return {
                    "dns": dns,
                    "m3u": f"{dns}/get.php?username={user}&password={password}&type=m3u_plus&output=ts",
                    "status": "✅ Ativo",
                    "info": f"Status: {status}"
                }
    except:
        pass
    return None

def run_mass_test(dns_list, user, password, threads, timeout):
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Criamos as tarefas de teste
        futures = [executor.submit(validate_dns_credentials, d, user, password, timeout) for d in dns_list]
        for f in futures:
            res = f.result()
            if res:
                results.append(res)
    return results
