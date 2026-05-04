import requests
from concurrent.futures import ThreadPoolExecutor

def validate_single_dns(dns, user, password, timeout=5):
    dns = dns.strip().rstrip('/')
    if not dns.startswith('http'): 
        dns = 'http://' + dns
    
    url = f"{dns}/player_api.php?username={user}&password={password}"
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            if data.get("user_info", {}).get("auth") == 1:
                return {
                    "dns": dns,
                    "status": "Online",
                    "exp": data["user_info"].get("exp_date", "N/A")
                }
    except:
        pass
    return None

def run_mass_test(dns_list, user, password, threads, timeout):
    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Passa os argumentos fixos usando uma função lambda ou partial
        futures = [executor.submit(validate_single_dns, d, user, password, timeout) for d in dns_list]
        for f in futures:
            res = f.result()
            if res:
                results.append(res)
    return results
