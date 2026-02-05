import os
import requests
from typing import List, Dict
from dotenv import load_dotenv


# ==============================
# Configuration
# ==============================

#TOKEN_URL = "https://api.francetravail.io/connexion/oauth2/access_token"
TOKEN_URL = "https://entreprise.francetravail.io/connexion/oauth2/access_token"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"


# ==============================
# Authentification
# ==============================

def get_france_travail_token() -> str:
    """
    Récupère un access_token OAuth2 via client_credentials
    """

    load_dotenv()

    client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
    client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise RuntimeError("FRANCE_TRAVAIL_CLIENT_ID ou CLIENT_SECRET manquant")

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "api_offresdemploiv2 o2dsoffre"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        timeout=15
    )

    response.raise_for_status()
    return response.json()["access_token"]


# ==============================
# Fetch offres
# ==============================

def fetch_france_travail_offers(
    token: str,
    keyword: str,
    limit: int = 20,
    contract_type: str | None = None,
    commune_insee: str | None = None
) -> List[Dict]:
    """
    Recherche des offres France Travail
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    params = {
        "motsCles": keyword,
        "range": f"0-{limit - 1}"
    }

    if contract_type:
        params["typeContrat"] = contract_type  # ex: CDI

    if commune_insee:
        params["commune"] = commune_insee  # code INSEE uniquement

    response = requests.get(
        SEARCH_URL,
        headers=headers,
        params=params,
        timeout=20
    )

    response.raise_for_status()
    data = response.json()
    return data.get("resultats", [])


# ==============================
# Normalisation (Airtable-ready)
# ==============================

def normalize_offer(raw_offer: Dict) -> Dict:
    """
    Normalise une offre France Travail vers le schéma minimal Airtable
    """
    return {
        "title": raw_offer.get("intitule"),
        "url": raw_offer.get("origineOffre", {}).get("urlOrigine"),
        "source": "France Travail"
    }


# ==============================
# Test manuel
# ==============================

if __name__ == "__main__":
    print("→ Test fetch France Travail")

    token = get_france_travail_token()
    offers = fetch_france_travail_offers(
        token=token,
        keyword="ingénieur chimiste",
        limit=10,
        contract_type="CDI"
    )

    print(f"{len(offers)} offre(s) trouvée(s)\n")

    for o in offers:
        clean = normalize_offer(o)
        print("—")
        print("Title :", clean["title"])
        print("URL   :", clean["url"])
