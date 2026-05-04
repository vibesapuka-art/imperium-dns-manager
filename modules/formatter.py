def build_dns_js(online_list):
    """
    Recebe uma lista de dicionários e retorna a string formatada:
    module.exports = ["dns1", "dns2"];
    """
    if not online_list:
        return ""
    
    lines = ["module.exports = ["]
    for item in online_list:
        lines.append(f'    "{item["dns"]}",')
    
    # Remove a vírgula do último item
    lines[-1] = lines[-1].rstrip(',')
    lines.append("];")
    
    return "\n".join(lines)
