from fetch_francetravail import fetch_france_travail

if __name__ == "__main__":
    offers = fetch_france_travail(
        keyword="chimie",
        location="94"  # Val-de-Marne
    )

    print(f"{len(offers)} offre(s) trouvée(s)\n")

    for o in offers[:5]:
        print("----")
        print("Titre     :", o["title"])
        print("Entreprise:", o["company"])
        print("Ville     :", o["city"])
        print("Contrat   :", o["contract"])
        print("URL       :", o["url"])
