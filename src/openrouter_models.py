"""OpenRouter models fetching module."""

import requests


def fetch_20_most_popular_openrouter_models(paid=False):
    """Fetch the 20 most popular models from OpenRouter.

    Args:
        paid: If True, fetch paid models only.

    Returns:
        Dictionary mapping formatted model names to model slugs.
    """
    url = (
        "https://openrouter.ai/api/frontend/models/find?"
        "order=most-popular&input_modalities=text&max_price=0&"
        "output_modalities=text"
    )
    if paid:
        url = (
            "https://openrouter.ai/api/frontend/models/find?"
            "order=most-popular&input_modalities=text&min_price=0.01&"
            "output_modalities=text"
        )
    try:
        data = (
            requests.get(url, headers={"Accept": "application/json"})
            .json()
            .get("data", {})
        )
    except Exception:  # noqa: BLE001
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

        # ZABEZPIECZENIE: Używamy "or {}" na wypadek
        # gdyby "endpoint" był równy None
        endpoint = m.get("endpoint") or {}
        pricing = endpoint.get("pricing") or {}

        if "prompt" in pricing and "completion" in pricing:
            popularity = analytics.get(m.get("permaslug"), {}).get(
                "total_prompt_tokens", 0
            )
            total_popularity += popularity

            p_price = float(pricing["prompt"]) * 1_000_000
            c_price = float(pricing["completion"]) * 1_000_000

            valid_models.append((m.get("slug"), popularity, p_price, c_price))

    # 2. Sortowanie modeli malejąco według popularności
    valid_models.sort(key=lambda x: x[1], reverse=True)

    # 3. Formatowanie i tworzenie docelowego słownika
    result = {}
    for slug, pop, p_price, c_price in valid_models[:20]:
        percent = (pop / max(total_popularity, 1)) * 100
        # Format prices with appropriate precision
        # Use .4f for small prices, .2f for larger ones
        p_price_str = f"{p_price:.4f}" if p_price < 0.01 else f"{p_price:.2f}"
        c_price_str = f"{c_price:.4f}" if c_price < 0.01 else f"{c_price:.2f}"
        formatted_name = f"{percent:>5.1f}% {slug:<40}\t[${p_price_str}/${c_price_str}]"
        result[formatted_name] = slug

    return result
