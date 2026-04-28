# ══════════════════════════════════════════════════════════════
# Stage 1 — Builder
# Image DHI Node avec shell pour installer et builder
# ══════════════════════════════════════════════════════════════
FROM dhi.io/node:24-debian13-dev AS builder

WORKDIR /app

# Copier les fichiers de dépendances
COPY package*.json ./

# Installer toutes les dépendances
RUN npm ci --legacy-peer-deps

# Copier le code source et builder
COPY . .
RUN npm run build

# ══════════════════════════════════════════════════════════════
# Stage 2 — Runtime
# Image DHI distroless — pas de shell, surface d'attaque minimale
# Nuxt produit un bundle autonome dans .output/
# Aucun node_modules nécessaire en runtime
# ══════════════════════════════════════════════════════════════
FROM dhi.io/node:24-debian13 AS runtime

WORKDIR /app

# Copier uniquement le bundle de production Nuxt
# .output/ contient tout le nécessaire, node_modules inclus
COPY --from=builder /app/.output /app/.output

USER node

EXPOSE 3000

CMD ["node", "/app/.output/server/index.mjs"]
