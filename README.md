# 🗓️ Planning Automatisé pour Entreprise

Un script Python MVP permettant de générer automatiquement un planning hebdomadaire équilibré pour une petite entreprise (ex. pharmacie), en prenant en compte les contraintes de disponibilités, de vacances, de jours préférés et d'équilibrage horaire.

---

## ✨ Fonctionnalités

- ✅ Multi-assignation par shift (plusieurs employés par créneau)
- ✅ Gestion fine des contraintes :
  - jours off (non travaillés)
  - jours de vacances (matin, après-midi, journée)
  - jours assignés obligatoires (matin, après-midi, journée)
- ✅ Respect des contrats horaires hebdomadaires
- ✅ Équilibrage des heures entre les employés
- ✅ Export CSV du planning et du bilan horaire

---

## 📚 Exemple de données

```python
employees = {
    "Alice": {
        "weekly_hours": 20,
        "days_off": [],
        "vacation_days": [("Mercredi", "matin")],
        "assigned_days": [("Lundi", "matin"), ("Vendredi", "apres-midi")]
    },
    ...
}

business_schedule = {
    "Lundi": [("08:00", "12:00"), ("14:00", "18:00")],
    ...
}

required_employees_per_day = {
    "Lundi": 2,
    "Mardi": 2,
    ...
}
```

---

## ⚡ Comment l'utiliser

1. Ouvrir le script dans un notebook Jupyter ou sur [Kaggle](https://kaggle.com)
2. Modifier les données d’entrée dans les blocs `employees`, `business_schedule` et `required_employees_per_day`
3. Exécuter le notebook
4. Visualiser le planning + bilan ou récupérer les CSV générés :
   - `planning.csv` : planning complet avec jour, horaires, employés
   - `bilan_employes.csv` : total des heures assignées par employé

💡 Les fichiers sont sauvegardés dans le répertoire de travail courant, accessibles dans l’interface Kaggle (onglet *Files*).

---

## 📚 Organisation du code

- `validate_data_consistency` : vérifie que les données sont cohérentes (jours connus, heures suffisantes, etc.)
- `generate_multi_shifts_with_moments` : crée la liste des shifts à couvrir en fonction du planning hebdomadaire
- `build_multi_scheduler` : définit les contraintes de planification et utilise un solveur pour générer les solutions valides
- `select_best_balanced_solution` : sélectionne la solution où la répartition des heures est la plus équilibrée entre les employés

---

## ❌ Limites actuelles

- Pas encore d'interface utilisateur graphique
- Aucune gestion de préférences souples (actuellement toutes les contraintes sont dures)
- Optimisation possible limitée à des cas de petite à moyenne taille

---

## 🚀 Prochaines évolutions après le MVP

- Ajout d'une **web app** pour faciliter l’usage par les utilisateurs non techniques
- Intégration des **préférences de planning** avec pondération (ex. préférences horaires, jours favoris)
- Ajout d’un export **Excel avec mise en forme visuelle**
- Tests unitaires & amélioration des performances du solveur

---

## © Auteur

Projet développé par **Frédéric CELERSE** (2025)
