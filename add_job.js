/* Ce bookmarklet permet d’ajouter rapidement une offre d’emploi à la base Airtable GenAI Jobs directement depuis la page de l’offre.
Concrètement, lorsqu’il est exécuté depuis une page d’annonce (LinkedIn, Indeed, 
France Travail, etc.), le script :
- récupère automatiquement l’URL de la page courante ;
- récupère le titre de la page (généralement le titre du poste) ;
- détecte la source de l’offre en fonction du site visité (LinkedIn, Indeed, France Travail ou autre) ;
- ouvre un formulaire Airtable prérempli avec ces informations.
L’utilisateur n’a alors plus qu’à vérifier ou compléter les champs (entreprise, localisation, type de contrat, etc.) avant de soumettre le formulaire.
L’offre est ainsi ajoutée instantanément à la table Airtable et peut ensuite être traitée par le pipeline GenAI Jobs (génération de CV, lettre, suivi de candidature).
*/

javascript:(function(){
    // 1. Extraire les infos d'Indeed (sélecteurs à vérifier selon la page)
    const jobTitle = document.querySelector('h1')?.innerText || "";
    const jobUrl = window.location.href;

    // 2. Construire l'URL Airtable avec les pré-remplissages
    const baseUrl = "https://airtable.com/appUKrvy2PHHC5opA/pagltQLktTbUy0oKe/form";
    const finalUrl = baseUrl + 
        "?prefill_title=" + encodeURIComponent(jobTitle) +
        "&prefill_URL=" + encodeURIComponent(jobUrl);

    // 3. Ouvrir dans un nouvel onglet
    window.open(finalUrl, '_blank');
})();