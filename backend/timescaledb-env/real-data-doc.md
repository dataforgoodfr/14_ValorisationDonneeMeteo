## Fichier de données réel 2025

Le fichier `real_data_2025.parquet` contient des données météorologiques réelles pour l'année 2025.

### Contenu du fichier

- **Format** : Parquet (format colonne optimisé pour le stockage et l'analyse)
- **Période couverte** : 1er janvier 2025 au 3 janvier 2026
- **Nombre d'enregistrements** : 35 242 observations horaires
- **Stations météorologiques** : 4 stations françaises principales
- **Variables météorologiques** : 204 colonnes incluant mesures et indicateurs de qualité

### Stations incluses

- **75114001** : Paris-Montsouris
- **33281001** : Bordeaux-Mérignac  
- **51449002** : Reims-Prunay
- **67124001** : Strasbourg-Entzheim

### Variables principales

#### Identifiants et localisation
- `NUM_POSTE` : Identifiant unique de la station (8 caractères)
- `NOM_USUEL` : Nom de la station
- `LAT`, `LON` : Coordonnées géographiques (degrés décimaux)
- `ALTI` : Altitude (mètres)

#### Temporel
- `AAAAMMJJHH` : Date et heure de l'observation (format datetime)

#### Températures (°C)
- `T` : Température de l'air
- `TD` : Température du point de rosée
- `TN` : Température minimale
- `TX` : Température maximale
- `T10`, `T20`, `T50`, `T100` : Températures du sol à différentes profondeurs

#### Humidité
- `U` : Humidité relative (%)
- `UN` : Humidité relative minimale (%)
- `UX` : Humidité relative maximale (%)

#### Vent
- `FF` : Vitesse moyenne du vent (m/s)
- `DD` : Direction du vent (°, 0=Nord, 90=Est)
- `FXY` : Rafale maximale (m/s)
- `DXY` : Direction de la rafale maximale (°)

#### Précipitations
- `RR1` : Précipitations horaires (mm)

#### Pression atmosphérique
- `PMER` : Pression au niveau de la mer (hPa)
- `PSTAT` : Pression station (hPa)

#### Visibilité et nébulosité
- `VV` : Visibilité (mètres)
- `N` : Nébulosité totale (0-8, 0=ciel clair, 8=ciel couvert)
- `NBAS` : Nébulosité des nuages bas

#### Rayonnement
- `GLO` : Rayonnement global (W/m²)
- `DIR` : Rayonnement direct (W/m²)
- `DIF` : Rayonnement diffus (W/m²)
- `UV` : Index UV
- `INS` : Rayonnement solaire (W/m²)

#### Qualité des données
Toutes les variables de mesure sont accompagnées de leur indicateur de qualité correspondant (préfixe `Q`), où :
- `Q* = 1` : Donnée valide
- `Q* = 0` ou autre : Donnée manquante ou suspecte

### Normes de gouvernance des données 2026

Ce jeu de données respecte les principes suivants :

1. **Traçabilité** : Chaque observation est horodatée et associée à une station identifiée
2. **Qualité** : Indicateurs de qualité systématiques pour chaque mesure
3. **Interopérabilité** : Format Parquet standardisé pour l'échange de données
4. **Métadonnées** : Documentation complète des variables et de leur signification
5. **Sécurité** : Données anonymisées (pas d'informations personnelles)
6. **Conformité RGPD** : Pas de données sensibles ou identifiantes

### Limitations et précautions

- Les données sont fournies "en l'état" sans garantie d'exhaustivité
- Certaines périodes peuvent avoir des lacunes de données
- Toujours vérifier les indicateurs de qualité avant analyse
- Les données ne doivent pas être utilisées pour des décisions critiques sans validation supplémentaire
