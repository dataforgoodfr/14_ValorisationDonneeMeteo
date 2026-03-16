# Frontend - ValoMeteo

## Lancer le projet

### Installation

#### Installation des dépendances

```bash
cd frontend
npm install
```

#### Mise en place de l'environnement

```bash
cd frontend
cp .env.example .env
```

### Développement

```bash
cd frontend
npm run dev
```

L'application est accessible sur `http://localhost:3000`

### Pre-commit

#### Installation

Les dépendances nécessaires sont installées automatiquement avec `npm install`.

#### Utilisation

Pour exécuter les hooks frontend uniquement depuis la racine du projet :

```bash
# Méthode 1: Utiliser npm run check (recommandé)
cd frontend
npm run check
```

**Note** : Les commandes utilisent `npx` pour exécuter les outils installés localement dans `node_modules`.

#### Résolution des problèmes

Si vous obtenez "eslint: command not found" :

```bash
cd frontend
npm install --legacy-peer-deps
```

Cela installera toutes les dépendances nécessaires dans `node_modules`.

### Production

```bash
cd frontend
npm run build
npm run preview  # Prévisualisation locale du build
```

## Stack technique

| Technologie                                   | Version | Usage                       |
| --------------------------------------------- | ------- | --------------------------- |
| [Nuxt](https://nuxt.com/)                     | 4.x     | Framework Vue.js full-stack |
| [Vue.js](https://vuejs.org/)                  | 3.5     | Framework réactif           |
| [TypeScript](https://www.typescriptlang.org/) | 5.x     | Typage statique             |
| [Tailwind CSS](https://tailwindcss.com/)      | 4.x     | Framework CSS utility-first |

## Modules Nuxt

Le projet tire parti de l'écosystème Nuxt via ses modules officiels :

| Module                                                            | Usage                                                                |
| ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| [@nuxt/ui](https://ui.nuxt.com/)                                  | Composants UI prêts à l'emploi (boutons, formulaires, modales...)    |
| [@nuxt/image](https://image.nuxt.com/)                            | Optimisation automatique des images (lazy loading, formats modernes) |
| [@nuxt/fonts](https://fonts.nuxt.com/)                            | Gestion optimisée des polices (chargement performant)                |
| [@nuxt/eslint](https://eslint.nuxt.com/)                          | Configuration ESLint intégrée                                        |
| [@nuxt/test-utils](https://nuxt.com/docs/getting-started/testing) | Utilitaires de test                                                  |
| [@nuxt/echarts](https://nuxt.com/docs/getting-started/testing)    | Nuxt Module for Apache ECharts                                       |

## Visualisation des données

Pour les graphiques, le projet utilise :

| Librairie                                        | Usage recommandé                                                      |
| ------------------------------------------------ | --------------------------------------------------------------------- |
| [Nuxt Echarts](https://nuxt.com/modules/echarts) | An Open Source JavaScript Visualization Library                       |
| [Chart.js](https://www.chartjs.org/)             | Graphiques standards (courbes, barres, camemberts) - Simple et rapide |
| [D3.js](https://d3js.org/)                       | Visualisations complexes et personnalisées (cartes, animations)       |

### Quand utiliser quoi ?

Utiliser Echarts par défaut. Les autres librairies serviront si des cas très spécifiques se présentent.

## Architecture du projet

```
frontend/
├── app/
│   ├── components/       # Composants Vue réutilisables
│   │   ├── layout/       # Header, Footer, Navigation
│   │   ├── charts/       # Composants de graphiques
│   │   └── ui/           # Composants UI spécifiques
│   ├── composables/      # Logique réutilisable (hooks)
│   ├── pages/            # Routes de l'application (file-based routing)
│   ├── assets/           # Fichiers statiques (CSS, images)
│   ├── app.vue           # Composant racine
│   └── app.config.ts     # Configuration de l'app
├── public/               # Fichiers servis tels quels (favicon...)
├── nuxt.config.ts        # Configuration Nuxt
└── package.json
```

### Conventions de nommage

- **Composants** : PascalCase (`MeteoChart.vue`, `TemperatureCard.vue`)
- **Composables** : camelCase avec préfixe `use` (`useMeteoData.ts`)
- **Pages** : kebab-case (`indicateurs-thermique.vue`)

## Lancer le Backend

### Prerequis

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) pour la gestion des dependances
- Docker (pour TimescaleDB)

### Installation

```bash
cd backend

# Installer les dependances, ainsi que les dépendances optionnelles de dev
uv sync --extra dev

# Copier la configuration
cp .env.example .env
```

### Données Simulées

Il est possible de lancer le projet sans utiliser de base de données.
Les données servies par l'API sont alors des données simulées.
Pour ce faire, mettre dans le fichier `.env` du repertoire `/backend`:

```
MOCKED_DATA=true
```

Si au contraire on souhaite utiliser une vraie base de données, voir la section correspondante sur le `README.md` du repertoire `/backend`.

## Demarrer TimescaleDB

```bash
cd timescaledb-env
docker compose up -d
cd ..
```

## Lancer le serveur

```bash
# Demarrer le serveur de developpement
uv run python manage.py runserver
```
