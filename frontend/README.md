# Frontend - ValoMeteo

## Lancer le projet

### Installation

```bash
npm install
```

### Développement

```bash
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

## Visualisation des données

Pour les graphiques, le projet utilise :

| Librairie                            | Usage recommandé                                                      |
| ------------------------------------ | --------------------------------------------------------------------- |
| [Chart.js](https://www.chartjs.org/) | Graphiques standards (courbes, barres, camemberts) - Simple et rapide |
| [D3.js](https://d3js.org/)           | Visualisations complexes et personnalisées (cartes, animations)       |

### Quand utiliser quoi ?

- **Chart.js** : Pour des graphiques classiques avec peu de personnalisation (températures sur le temps, comparaisons)
- **D3.js** : Pour des visualisations sur mesure (cartes météo interactives, animations de données)

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

## Récupération des données (Data Fetching)

Nuxt propose plusieurs méthodes pour récupérer des données depuis le backend. **Privilégier les composables Nuxt** plutôt que `fetch` natif.

### `useFetch` - Cas standard

Le composable principal pour récupérer des données. Gère automatiquement :

- Le SSR (pas de double requête serveur/client)
- Les états de chargement et d'erreur
- La réactivité

```vue
<script setup lang="ts">
// Récupération simple
const { data, status, error } = await useFetch("/api/meteo/temperatures");

// Avec paramètres réactifs
const ville = ref("paris");
const { data: meteo } = await useFetch(() => `/api/meteo/${ville.value}`);
</script>

<template>
  <div v-if="status === 'pending'">Chargement...</div>
  <div v-else-if="error">Erreur : {{ error.message }}</div>
  <div v-else>{{ data }}</div>
</template>
```

### `useAsyncData` - Contrôle avancé

Pour plus de contrôle sur la logique de récupération :

```vue
<script setup lang="ts">
const { data } = await useAsyncData("temperatures", async () => {
  const [temps, humidite] = await Promise.all([
    $fetch("/api/temperatures"),
    $fetch("/api/humidite"),
  ]);
  return { temps, humidite };
});
</script>
```

### `$fetch` - Actions utilisateur

Pour les requêtes déclenchées par l'utilisateur (soumission de formulaire, bouton) :

```vue
<script setup lang="ts">
async function exporterDonnees() {
  const result = await $fetch("/api/export", {
    method: "POST",
    body: { format: "csv" },
  });
}
</script>
```

### Bonnes pratiques

- **Ne jamais utiliser `fetch` natif** dans les composants Vue → utiliser `useFetch` ou `$fetch`
- **`useFetch`** pour les données affichées au chargement de la page
- **`$fetch`** pour les actions utilisateur (POST, PUT, DELETE)
- **Typer les réponses** pour bénéficier de l'autocomplétion

## Points d'attention à arbitrer

- **Performance** : La mise en place d'une pagination ou d'un lazy loading pourrait s'avérer nécessaire.
