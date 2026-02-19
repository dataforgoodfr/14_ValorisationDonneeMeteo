# Valorisation Donnée Météo

Projet Data For Good - Saison 14

## Structure du projet

```
├── backend/    # API et traitement des données (Python)
├── frontend/   # Interface utilisateur
```

## Pour commencer

Consultez les README de chaque sous-projet :

- [Backend](backend/README.md)
- [Frontend](frontend/README.md)

## Contribuer

Ce projet fait partie de la saison 14 de Data For Good.

## Utilisation de Git

Le projet utilise la branche `main` comme branche principale.

## Workflow de contribution

Lire attentivement nos bonnes pratiques de développement : [Branches et commits : Workflow de contribution](https://outline.services.dataforgood.fr/doc/onboarding-dev-OFGKWOcxOn)

Extraits :

### :tanabata_tree:Branches et commits : Workflow de contribution

Pour que tout le monde adopte les mêmes pratiques, nous avons posé des principes relatifs aux branches et aux commits. A lire impérativement avant de commencer.

#### 0. **Paramétrer git**

```bash
git config --local pull.rebase merges
git config --local rebase.autostash true
```

- `pull.rebase merges` applique vos commits locaux par-dessus le remote.
- `rebase.autostash true` permet de stasher automatiquement vos changements locaux non commités avant de faire un pull/rebase, et de les réappliquer après. Cela évite les conflits liés à des changements locaux non commités lors du pull/rebase.

#### 1. **Créer une branche depuis** `**main**`

```bash
git checkout main
git pull origin main
git checkout -b <type>/(<scope>/)?<description-courte>
```

Convention de nommage des branches :

* `feat/scope/nom-feature` : nouvelle fonctionnalité
* `fix/scope/nom-bug` : correction de bug
* `docs/sujet` : documentation
* `refactor/sujet` : refactoring de code
* `chore/sujet` : tâche de maintenance

Exemple : `feat/itn/ajout-carte-meteo` ou `fix/ecarts-normales/erreur-chargement-donnees`

#### 2. **Faire des commits atomiques**

Un commit atomique = une seule modification logique. Cela permet de :

* Faciliter la relecture du code
* Simplifier un éventuel rollback
* Garder un historique clair

```bash
git add <fichiers-concernés>
git commit -m "<type>: (<scope>:)? <description>"
```

Format des messages de commit :

* `feat: itn: ajoute le composant carte météo`
* `fix: ecarts normales: corrige l'affichage des températures négatives`
* `docs: readme: mise à jour installation`
* `refactor: parser: simplifie la logique de parsing`
* `test: parser: ajoute les tests unitaires`
* `chore: npm: met à jour les dépendances`

Vous n'êtes pas obligé d'utiliser le terminal, vous pouvez utiliser n'importe quelle interface graphique, notamment celle de VSCode et JetBrains.

#### 3. **Pousser sa branche et créer une Pull Request (PR)**

```bash
git push origin <nom-de-ta-branche>
```

Puis sur GitHub, créer une PR vers `main` en :

* Donnant un titre clair et descriptif
* Remplissant le template de PR
* Assignant des reviewers

#### 4. **Review de code**

Chaque PR doit être relue par au moins une personne avant d'être mergée.

En tant que reviewer :

* Vérifier que le code fonctionne et respecte les conventions du projet
* Poser des questions si quelque chose n'est pas clair
* Proposer des améliorations de manière constructive

En tant qu'auteur :

* Répondre aux commentaires
* Effectuer les modifications demandées
* Demander une nouvelle review si nécessaire

#### 5. **Merge avec squash commit**

Une fois la PR approuvée, on merge en utilisant **"Squash and merge"** sur GitHub. Cela combine tous les commits de la branche en un seul commit sur `main`, ce qui garde un historique propre.

### Bonnes pratiques

* **Synchroniser régulièrement** sa branche avec `main` pour éviter les conflits :

```bash
git checkout main
git pull origin main
git checkout <ta-branche>
git rebase main
```

* **Ne jamais pusher directement sur** `**main**`
* **Garder ses PRs petites** : une PR = une fonctionnalité ou un fix. Les grosses PRs sont difficiles à relire
* **Tester son code** avant de pousser

### :male_technologist:Éditeur de code

Nous conseillons (surtout pour les débutants) de travailler avec [Visual Studio Code](https://code.visualstudio.com/) (VSCode pour les intimes).
Voici un [tuto](https://data-for-good.slack.com/archives/C08B329AG7M/p1738330293159749) pour l'usage de VSCode, l’installation de Python, et faire tourner son premier notebook dans VSCode.

Pour les plus avancés, nous conseillons la suite JetBrains, notamment WebStorm et PyCharm en version gratuite.

Pensez à activer le formattage et le fix automatique lors de la sauvegarde :

- [VSCode](.vscode/settings.json)
- JetBrains : Tools → Actions on Save :
  - Reformat Code
  - Optimize Imports
  - Run eslint --fix
  - Run Prettier

## Installation des pre-commit hooks

Ce projet utilise [pre-commit](https://pre-commit.com/) pour automatiser la vérification de la qualité du code avant chaque commit.

### Installer pre-commit sur votre machine

#### Via pip

```bash
pip install pre-commit
```

### Activer les hooks

```bash
# À la racine du projet
pre-commit install
```

### Configuration

Le projet utilise deux configurations de pre-commit :

1. **Configuration racine** (`.pre-commit-config.yaml`) :
   - Exécute les hooks backend et frontend
   - Vérifie les conflits de merge, les fins de ligne, etc.

2. **Configuration backend** (`backend/.pre-commit-config.yaml`) :
   - Utilise Ruff pour le linting et le formatting Python
   - Ignore le code DJ001 (docstring pour les classes privées)

### Exécution manuelle

Pour exécuter tous les hooks sur tous les fichiers :

```bash
pre-commit run --all-files
```

Pour exécuter uniquement les hooks backend :

```bash
cd backend && uv run pre-commit run --all-files --config=.pre-commit-config.yaml
```

Pour exécuter uniquement les hooks frontend :

```bash
cd frontend && npm run check
```

### Résolution des problèmes courants

#### Problème d'environnement Node.js

Si vous obtenez une erreur "eslint: command not found" :

```bash
cd frontend
npm install --legacy-peer-deps
```

### Outils utilisés

- **Backend** : Ruff (linting + formatting)
- **Frontend** : ESLint + Prettier
- **Commun** : vérification des conflits, fins de ligne, etc.
