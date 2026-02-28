import requests

def fetch_20_most_popular_openrouter_models():
    try:
        url = "https://openrouter.ai/api/frontend/models/find?order=most-popular"
        data = requests.get(url, headers={"Accept": "application/json"}).json().get("data", {})
    except Exception:
        print("Failed to fetch or parse OpenRouter data")
        return {}

    models = data.get("models", [])
    analytics = data.get("analytics", {})
    
    valid_models = []
    total_popularity = 0

    # 1. Filtrowanie modeli i zbieranie danych
    for m in models:
        if not isinstance(m, dict):
            continue
            
        # ZABEZPIECZENIE: Używamy "or {}" na wypadek gdyby "endpoint" był równy None
        endpoint = m.get("endpoint") or {}
        pricing = endpoint.get("pricing") or {}
        
        if "prompt" in pricing and "completion" in pricing:
            popularity = analytics.get(m.get("permaslug"), {}).get("total_prompt_tokens", 0)
            total_popularity += popularity
            
            p_price = float(pricing["prompt"]) * 1_000_000
            c_price = float(pricing["completion"]) * 1_000_000
            
            valid_models.append((m.get("slug"), popularity, p_price, c_price))

    # 2. Sortowanie modeli malejąco według popularności (indeks 1 w krotce)
    valid_models.sort(key=lambda x: x[1], reverse=True)

    # 3. Formatowanie i tworzenie docelowego słownika (tylko 20 pierwszych wyników)
    result = {}
    for slug, pop, p_price, c_price in valid_models[:20]:
        percent = (pop / max(total_popularity, 1)) * 100
        formatted_name = f"{percent:04.1f}% {slug}\t[${p_price:.2f}/${c_price:.2f}]"
        result[formatted_name] = slug

    return result
