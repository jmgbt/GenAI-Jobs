# GenAI Jobs

GenAI Jobs est un projet expérimental visant à automatiser **une partie du traitement des offres d’emploi** à l’aide de l’IA, en adoptant une approche volontairement simple et pragmatique.

Cette V0 repose sur une architecture **Airtable-first**, sans frontend dédié ni backend lourd.

---

## 🎯 Objectif de la V0

- Centraliser des offres d’emploi dans Airtable
- Laisser un délai (ex. 24h) pour décider d’un traitement manuel
- Passé ce délai, déclencher automatiquement un **worker IA**
- Générer une lettre de motivation adaptée à l’offre
- Journaliser le statut et le résultat du traitement

Cette version ne cherche **pas** à postuler automatiquement aux offres, mais à valider la logique et la valeur du flux IA.

---

## 🧠 Architecture (V0)

