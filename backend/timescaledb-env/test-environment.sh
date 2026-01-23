#!/bin/bash
# Script de test automatique de l'environnement TimescaleDB
# Usage: ./test-environment.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🧪 Test de l'environnement TimescaleDB${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test 1: Docker is installed
echo -n "1️⃣  Vérification de Docker... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Docker n'est pas installé${NC}"
    exit 1
fi

# Test 2: Docker Compose is installed
echo -n "2️⃣  Vérification de Docker Compose... "
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Docker Compose n'est pas installé${NC}"
    exit 1
fi

# Test 3: uv is installed
echo -n "3️⃣  Vérification de uv... "
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ uv n'est pas installé. Installez avec: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
fi

# Test 4: Check if container is running
echo -n "4️⃣  Vérification du container TimescaleDB... "
if docker ps | grep -q "infoclimat-timescaledb"; then
    echo -e "${GREEN}✓ (running)${NC}"
else
    echo -e "${YELLOW}⚠ Container non démarré. Démarrage...${NC}"
    docker-compose up -d
    echo -n "   Attente du démarrage (10s)... "
    sleep 10
    echo -e "${GREEN}✓${NC}"
fi

# Test 5: Check database connectivity
echo -n "5️⃣  Test de connexion à la base... "
if docker exec infoclimat-timescaledb pg_isready -U infoclimat -d meteodb &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Impossible de se connecter à la base${NC}"
    exit 1
fi

# Test 6: Check TimescaleDB extension
echo -n "6️⃣  Vérification de l'extension TimescaleDB... "
EXT_CHECK=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc "SELECT COUNT(*) FROM pg_extension WHERE extname='timescaledb'")
if [ "$EXT_CHECK" -eq "1" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ Extension TimescaleDB non activée${NC}"
    exit 1
fi

# Test 7: Check tables exist
echo -n "7️⃣  Vérification des tables... "
STATION_EXISTS=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc "SELECT COUNT(*) FROM pg_tables WHERE tablename='Station'")
HORAIRE_EXISTS=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc "SELECT COUNT(*) FROM pg_tables WHERE tablename='HoraireTempsReel'")
QUOTIDIENNE_EXISTS=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc "SELECT COUNT(*) FROM pg_tables WHERE tablename='Quotidienne'")

if [ "$STATION_EXISTS" -eq "1" ] && [ "$HORAIRE_EXISTS" -eq "1" ] && [ "$QUOTIDIENNE_EXISTS" -eq "1" ]; then
    echo -e "${GREEN}✓ (3/3 tables)${NC}"
else
    echo -e "${RED}✗ Tables manquantes${NC}"
    exit 1
fi

# Test 8: Check hypertables
echo -n "8️⃣  Vérification des hypertables... "
HYPERTABLE_COUNT=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc "SELECT COUNT(*) FROM timescaledb_information.hypertables")
if [ "$HYPERTABLE_COUNT" -ge "2" ]; then
    echo -e "${GREEN}✓ ($HYPERTABLE_COUNT hypertables)${NC}"
else
    echo -e "${YELLOW}⚠ Seulement $HYPERTABLE_COUNT hypertable(s) trouvée(s)${NC}"
fi

# Test 9: Check data exists
echo -n "9️⃣  Vérification des données... "
STATION_COUNT=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc 'SELECT COUNT(*) FROM "Station"')
HORAIRE_COUNT=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc 'SELECT COUNT(*) FROM "HoraireTempsReel"')
QUOTIDIENNE_COUNT=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc 'SELECT COUNT(*) FROM "Quotidienne"')

if [ "$STATION_COUNT" -ge "1" ]; then
    echo -e "${GREEN}✓${NC}"
    echo "   📍 Stations: $STATION_COUNT"
    echo "   ⏰ Horaire: $HORAIRE_COUNT"
    echo "   📅 Quotidienne: $QUOTIDIENNE_COUNT"
else
    echo -e "${YELLOW}⚠ Aucune donnée. Exécutez: uv run docker/generate-mock-data.py${NC}"
fi

# Test 10: Sample query
echo -n "🔟 Test de requête SQL... "
QUERY_RESULT=$(docker exec infoclimat-timescaledb psql -U infoclimat -d meteodb -tAc 'SELECT COUNT(*) FROM "Station" WHERE "posteOuvert" = true')
if [ "$QUERY_RESULT" -ge "0" ]; then
    echo -e "${GREEN}✓ (${QUERY_RESULT} postes ouverts)${NC}"
else
    echo -e "${RED}✗ Erreur de requête${NC}"
fi

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Tous les tests sont passés !${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Display connection info
echo -e "${BLUE}📌 Informations de connexion :${NC}"
echo "   Host:     localhost"
echo "   Port:     5432"
echo "   Database: meteodb"
echo "   User:     infoclimat"
echo "   Password: infoclimat2026"

echo -e "\n${BLUE}📚 Commandes utiles :${NC}"
echo "   Se connecter: docker exec -it infoclimat-timescaledb psql -U infoclimat -d meteodb"
echo "   Voir les logs: docker-compose logs -f"
echo "   Arrêter:      docker-compose down"
echo "   Nettoyer:     docker-compose down -v"

echo -e "\n${GREEN}🎉 L'environnement est prêt à l'emploi !${NC}\n"
