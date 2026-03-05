# Documentation des champs meteorologiques

Ce document decrit les champs des modeles Django utilises pour stocker les donnees meteorologiques.
Toutes les definitions proviennent de la **documentation officielle Meteo-France**.

## Sources de reference

- **Meteo-France** : [Portail Donnees Publiques](https://donneespubliques.meteofrance.fr/)
- **Documentation locale** : `../telechargement-climatologie-portail-api-meteofrance/docs/mf/`
  - `observations/horaire.csv` - Champs des observations horaires temps reel
  - `donnees-horaires/H_descriptif_champs.csv` - Champs des donnees climatologiques horaires
  - `donnees-quotidiennes/Q_descriptif_champs_*.csv` - Champs des donnees quotidiennes
- **InfoClimat field reference**:
  - https://github.com/AssociationInfoclimat/telechargement-climatologie-portail-api-meteofrance/tree/main/docs/mf
  - https://github.com/AssociationInfoclimat/telechargement-climatologie-meteo-data-gouv/tree/main/docs/mf

---

## Conventions

### Codes qualite (Q*)

A chaque donnee est associe un code qualite (ex: T;QT). Valeurs possibles :

| Code | Signification |
|------|---------------|
| 0 | Donnee protegee (validee definitivement par le climatologue) |
| 1 | Donnee validee (validee par controle automatique ou par le climatologue) |
| 2 | Donnee douteuse en cours de verification (mise en doute par controle automatique) |
| 9 | Donnee filtree (a passe les filtres/controles de premiers niveaux) |

### Unites importantes - ATTENTION

Les unites varient selon la source des donnees :

| Parametre | API Observations (temps reel) | Donnees climatologiques |
|-----------|------------------------------|------------------------|
| Temperatures | **Kelvins (K)** | **°C et 1/10** |
| Pressions | **Pascals (Pa)** | **hPa et 1/10** |
| Neige (sss) | **metres (m)** | **cm** |
| Insolation | **minutes (min)** | **minutes (mn)** |
| Rayonnement | **J/m2** | **J/cm2** |

### Valeurs manquantes
- En base de donnees : `NULL`
- Dans les fichiers bruts Meteo-France : generalement non renseigne ou valeur speciale

---

## Modele `Station`

Metadonnees des stations meteorologiques.

| Champ | Type | Description | Source |
|-------|------|-------------|--------|
| `code` | CharField(8) | **NUM_POSTE** : numero Meteo-France du poste sur 8 chiffres. | Meteo-France |
| `nom` | TextField | **NOM_USUEL** : nom usuel du poste. | Meteo-France |
| `departement` | IntegerField | Code departement francais (01-95 metropole, 971-976 DOM). | INSEE |
| `frequence` | CharField(20) | Frequence des observations : "horaire", "quotidienne", "infrahoraire". | Meteo-France |
| `poste_ouvert` | BooleanField | Indique si la station est actuellement en activite. | Meteo-France |
| `type_poste` | IntegerField | Code type d'equipement de la station. | Meteo-France |
| `lon` | FloatField | **LON** : longitude, negative a l'ouest de Greenwich (en degres et millioniemes de degre). | Meteo-France |
| `lat` | FloatField | **LAT** : latitude, negative au sud (en degres et millioniemes de degre). | Meteo-France |
| `alt` | FloatField | **ALTI** : altitude du pied de l'abri ou du pluviometre si pas d'abri (en m). | Meteo-France |
| `poste_public` | BooleanField | Indique si les donnees de la station sont publiquement accessibles. | Meteo-France |

---

## Modele `HoraireTempsReel`

Mesures meteorologiques horaires en temps reel. Table TimescaleDB partitionnee par `validity_time`.

> **Note** : Ce modele correspond aux donnees de l'API Observations Meteo-France. Les unites sont celles de l'API (Kelvins, Pascals, metres).

### Champs d'identification

| Champ | Type | Description | Source |
|-------|------|-------------|--------|
| `station` | ForeignKey | Reference vers la station meteorologique. | - |
| `lat` | FloatField | Latitude du poste en degres. | Meteo-France |
| `lon` | FloatField | Longitude du poste en degres. | Meteo-France |
| `reference_time` | DateTimeField | Date et heure de la production des donnees (ISO 8601/UTC). | Meteo-France |
| `insert_time` | DateTimeField | Date et heure d'insertion des donnees dans la base de donnees (ISO 8601/UTC). | Meteo-France |
| `validity_time` | DateTimeField | **Date et heure de validite des donnees** (ISO 8601/UTC). Colonne de partitionnement TimescaleDB. | Meteo-France |

### Champs de temperature

| Champ | Type | Unite API | Description | Source |
|-------|------|-----------|-------------|--------|
| `t` | FloatField | K | **Temperature sous abri** en degres Kelvins. | Meteo-France |
| `td` | FloatField | K | **Point de rosee** a 2 metres au-dessus du sol en degres Kelvins. | Meteo-France |
| `tx` | FloatField | K | **Temperature maximale** de l'air a 2 metres au-dessus du sol en degres Kelvins. | Meteo-France |
| `tn` | FloatField | K | **Temperature minimale** de l'air a 2 metres au-dessus du sol en degres Kelvins. | Meteo-France |

### Champs d'humidite

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `u` | IntegerField | % | **Humidite relative** horaire. | Meteo-France |
| `ux` | IntegerField | % | **Humidite relative maximale** dans l'heure. | Meteo-France |
| `un` | IntegerField | % | **Humidite relative minimale** dans l'heure. | Meteo-France |

### Champs de vent

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `dd` | IntegerField | degres | **Direction de ff** en degres (rose de 360). | Meteo-France |
| `ff` | FloatField | m/s | **Force du vent moyen** sur 10 minutes a 10 metres au-dessus du sol. | Meteo-France |
| `dxy` | IntegerField | degres | **Direction de fxy** en degres (rose de 360). | Meteo-France |
| `fxy` | FloatField | m/s | 
    https://github.com/AssociationInfoclimat/telechargement-climatologie-portail-api-meteofrance/tree/main/docs/mf
    https://github.com/AssociationInfoclimat/telechargement-climatologie-meteo-data-gouv/tree/main/docs/mf
**Force maximale de FF dans l'heure** a 10 metres au-dessus du sol. | Meteo-France |
| `dxi` | IntegerField | degres | **Direction de fxi** en degres (rose de 360). | Meteo-France |
| `fxi` | FloatField | m/s | **Force maximale du vent instantane dans l'heure** a 10 metres au-dessus du sol. | Meteo-France |

### Champs de precipitation

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `rr1` | FloatField | mm | **Hauteur de precipitations dans l'heure**. | Meteo-France |

### Champs de temperature du sol

| Champ | Type | Unite API | Description | Source |
|-------|------|-----------|-------------|--------|
| `t_10` | FloatField | K | **Temperature a 10 centimetres de profondeur** sous le sol en degres Kelvins. | Meteo-France |
| `t_20` | FloatField | K | **Temperature a 20 centimetres de profondeur** sous le sol en degres Kelvins. | Meteo-France |
| `t_50` | FloatField | K | **Temperature a 50 centimetres de profondeur** sous le sol en degres Kelvins. | Meteo-France |
| `t_100` | FloatField | K | **Temperature a 100 centimetres de profondeur** (1 m) sous le sol en degres Kelvins. | Meteo-France |

### Autres mesures atmospheriques

| Champ | Type | Unite API | Description | Source |
|-------|------|-----------|-------------|--------|
| `vv` | IntegerField | m | **Visibilite horizontale** en metres. | Meteo-France |
| `etat_sol` | IntegerField | code | **Code de l'etat du sol** (voir tableau ci-dessous). | Meteo-France |
| `sss` | FloatField | m | **Hauteur totale de la couverture neigeuse** en metres. | Meteo-France |
| `n` | IntegerField | octas | **Nebulosite totale** en octas. 9 = ciel invisible par brouillard. | Meteo-France |
| `insolh` | FloatField | min | **Duree d'insolation** au cours de la periode en minutes. | Meteo-France |
| `ray_glo01` | FloatField | J/m2 | **Rayonnement global** sur l'heure. | Meteo-France |
| `pres` | FloatField | Pa | **Pression au niveau de la station** en Pascals. | Meteo-France |
| `pmer` | FloatField | Pa | **Pression au niveau de la mer** en Pascals. | Meteo-France |

### Code etat_sol (SOL) - Etat du sol sans neige

| Code | Description |
|------|-------------|
| 0 | Surface du sol seche (sans fissure et sans poussiere ni sable meuble en quantite appreciable) |
| 1 | Surface du sol humide |
| 2 | Surface du sol mouillee (eau stagnante en mares a la surface) |
| 3 | Inonde |
| 4 | Surface du sol gelee |
| 5 | Verglas au sol |
| 6 | Poussiere ou sable meuble sec ne couvrant pas completement le sol |
| 7 | Couche fine de poussiere ou de sable meuble couvrant completement le sol |
| 8 | Couche epaisse ou d'epaisseur moyenne de poussiere ou de sable meuble couvrant completement le sol |
| 9 | Tres sec avec fissures |

---

## Modele `Quotidienne`

Donnees meteorologiques agregees sur 24 heures. Table TimescaleDB partitionnee par `date`.

> **Note** : Ce modele correspond aux donnees climatologiques quotidiennes. Les unites sont en °C, hPa, etc.

### Champs d'identification

| Champ | Type | Description | Source |
|-------|------|-------------|--------|
| `station` | ForeignKey | Reference vers la station meteorologique. | - |
| `nom_usuel` | TextField | **NOM_USUEL** : nom usuel du poste. | Meteo-France |
| `lat` | FloatField | **LAT** : latitude, negative au sud (en degres et millioniemes de degre). | Meteo-France |
| `lon` | FloatField | **LON** : longitude, negative a l'ouest de Greenwich (en degres et millioniemes de degre). | Meteo-France |
| `alti` | FloatField | **ALTI** : altitude du pied de l'abri ou du pluviometre si pas d'abri (en m). | Meteo-France |
| `date` | DateField | **AAAAMMJJ** : date de la mesure. Colonne de partitionnement TimescaleDB. | Meteo-France |

### Precipitations

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `rr` | FloatField | mm et 1/10 | **RR** : quantite de precipitation tombee en 24 heures (de 06h FU le jour J a 06h FU le jour J+1). La valeur relevee a J+1 est affectee au jour J. | Meteo-France |
| `qrr` | IntegerField | code | Code qualite pour `rr`. | Meteo-France |
| `drr` | IntegerField | mn | **DRR** : duree des precipitations. | Meteo-France |
| `qdrr` | IntegerField | code | Code qualite pour `drr`. | Meteo-France |

### Temperatures

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `tn` | FloatField | °C et 1/10 | **TN** : temperature minimale sous abri. | Meteo-France |
| `qtn` | IntegerField | code | Code qualite pour `tn`. | Meteo-France |
| `htn` | CharField(4) | hhmm | **HTN** : heure de TN. | Meteo-France |
| `qhtn` | IntegerField | code | Code qualite pour `htn`. | Meteo-France |
| `tx` | FloatField | °C et 1/10 | **TX** : temperature maximale sous abri. | Meteo-France |
| `qtx` | IntegerField | code | Code qualite pour `tx`. | Meteo-France |
| `htx` | CharField(4) | hhmm | **HTX** : heure de TX. | Meteo-France |
| `qhtx` | IntegerField | code | Code qualite pour `htx`. | Meteo-France |
| `tm` | FloatField | °C et 1/10 | **TM** : moyenne quotidienne des temperatures horaires sous abri. | Meteo-France |
| `qtm` | IntegerField | code | Code qualite pour `tm`. | Meteo-France |
| `tntxm` | FloatField | °C et 1/10 | **TNTXM** : moyenne quotidienne (TN+TX)/2. | Meteo-France |
| `qtntxm` | IntegerField | code | Code qualite pour `tntxm`. | Meteo-France |
| `tampli` | FloatField | °C et 1/10 | **TAMPLI** : amplitude thermique quotidienne (TX-TN). | Meteo-France |
| `qtampli` | IntegerField | code | Code qualite pour `tampli`. | Meteo-France |

### Temperature du sol

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `tnsol` | FloatField | °C et 1/10 | **TNSOL** : temperature quotidienne minimale a 10 cm **au-dessus** du sol. | Meteo-France |
| `qtnsol` | IntegerField | code | Code qualite pour `tnsol`. | Meteo-France |
| `tn50` | FloatField | °C et 1/10 | **TN50** : temperature quotidienne minimale a 50 cm **au-dessus** du sol. | Meteo-France |
| `qtn50` | IntegerField | code | Code qualite pour `tn50`. | Meteo-France |

### Duree de gel

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `dg` | IntegerField | mn | **DG** : duree de gel sous abri (T <= 0°C) en minutes. | Meteo-France |
| `qdg` | IntegerField | code | Code qualite pour `dg`. | Meteo-France |

### Vent

| Champ | Type | Unite | Description | Source |
|-------|------|-------|-------------|--------|
| `ffm` | FloatField | m/s et 1/10 | **FFM** : moyenne quotidienne de la force du vent moyenne sur 10 mn, a 10 m. | Meteo-France |
| `qffm` | IntegerField | code | Code qualite pour `ffm`. | Meteo-France |
| `ff2m` | FloatField | m/s et 1/10 | **FF2M** : moyenne quotidienne de la force du vent moyenne sur 10 mn, a 2 m. | Meteo-France |
| `qff2m` | IntegerField | code | Code qualite pour `ff2m`. | Meteo-France |
| `fxy` | FloatField | m/s et 1/10 | **FXY** : maximum quotidien de la force maximale horaire du vent moyenne sur 10 mn, a 10 m. | Meteo-France |
| `qfxy` | IntegerField | code | Code qualite pour `fxy`. | Meteo-France |
| `dxy` | IntegerField | rose de 360 | **DXY** : direction de FXY. | Meteo-France |
| `qdxy` | IntegerField | code | Code qualite pour `dxy`. | Meteo-France |
| `hxy` | CharField(4) | hhmm | **HXY** : heure de FXY. | Meteo-France |
| `qhxy` | IntegerField | code | Code qualite pour `hxy`. | Meteo-France |
| `fxi` | FloatField | m/s et 1/10 | **FXI** : maximum quotidien de la force maximale horaire du vent instantane, a 10 m. | Meteo-France |
| `qfxi` | IntegerField | code | Code qualite pour `fxi`. | Meteo-France |
| `dxi` | IntegerField | rose de 360 | **DXI** : direction de FXI. | Meteo-France |
| `qdxi` | IntegerField | code | Code qualite pour `dxi`. | Meteo-France |
| `hxi` | CharField(4) | hhmm | **HXI** : heure de FXI. | Meteo-France |
| `qhxi` | IntegerField | code | Code qualite pour `hxi`. | Meteo-France |
| `fxi2` | FloatField | m/s et 1/10 | **FXI2** : maximum quotidien de la force maximale horaire du vent instantane, a 2 m. | Meteo-France |
| `qfxi2` | IntegerField | code | Code qualite pour `fxi2`. | Meteo-France |
| `dxi2` | IntegerField | rose de 360 | **DXI2** : direction de FXI2. | Meteo-France |
| `qdxi2` | IntegerField | code | Code qualite pour `dxi2`. | Meteo-France |
| `hxi2` | CharField(4) | hhmm | **HXI2** : heure de FXI2. | Meteo-France |
| `qhxi2` | IntegerField | code | Code qualite pour `hxi2`. | Meteo-France |
| `fxi3s` | FloatField | m/s et 1/10 | **FXI3S** : maximum quotidien de la force maximale horaire du vent moyenne sur 3 s, a 10 m. | Meteo-France |
| `qfxi3s` | IntegerField | code | Code qualite pour `fxi3s`. | Meteo-France |
| `dxi3s` | IntegerField | rose de 360 | **DXI3S** : direction de FXI3S. | Meteo-France |
| `qdxi3s` | IntegerField | code | Code qualite pour `dxi3s`. | Meteo-France |
| `hxi3s` | CharField(4) | hhmm | **HXI3S** : heure de FXI3S. | Meteo-France |
| `qhxi3s` | IntegerField | code | Code qualite pour `hxi3s`. | Meteo-France |

---

## Champs supplementaires (donnees climatologiques horaires)

Ces champs sont documentes dans la source Meteo-France mais ne sont pas tous presents dans le modele Django actuel.

### Temperatures supplementaires

| Champ | Unite | Description |
|-------|-------|-------------|
| TNSOL | °C et 1/10 | Temperature minimale a 10 cm au-dessus du sol |
| TN50 | °C et 1/10 | Temperature minimale a 50 cm au-dessus du sol |
| TCHAUSSEE | °C et 1/10 | Temperature de surface mesuree sur herbe ou sur bitume |
| TMER | °C et 1/10 | Temperature de la mer |

### Pression

| Champ | Unite | Description |
|-------|-------|-------------|
| PSTAT | hPa et 1/10 | Pression station |
| PMERMIN | hPa et 1/10 | Minimum horaire de la pression mer |
| GEOP | mgp | Geopotentiel (stations > 750 m d'altitude) |

### Humidite supplementaire

| Champ | Unite | Description |
|-------|-------|-------------|
| TSV | hPa et 1/10 | Tension de vapeur |
| DHUMEC | mn | Duree d'humectation |
| DHUMI40 | mn | Duree avec humidite <= 40% |
| DHUMI80 | mn | Duree avec humidite >= 80% |

### Nuages

| Champ | Unite | Description |
|-------|-------|-------------|
| NBAS | octa | Nebulosite de la couche nuageuse principale la plus basse |
| CL | code | Code SYNOP nuages bas |
| CM | code | Code SYNOP nuages moyens |
| CH | code | Code SYNOP nuages eleves |
| N1-N4 | octa | Nebulosite des couches nuageuses 1 a 4 |
| C1-C4 | code | Genre des couches nuageuses 1 a 4 |
| B1-B4 | m | Base des couches nuageuses 1 a 4 |

### Temps present et passe

| Champ | Description |
|-------|-------------|
| WW | Code descriptif du temps present (WMO table 4677) |
| W1 | Code descriptif du temps passe 1 (WMO table 4687) |
| W2 | Code descriptif du temps passe 2 (WMO table 4687) |

### Neige

| Champ | Unite | Description |
|-------|-------|-------------|
| HNEIGEF | cm | Hauteur de neige fraiche tombee en 6h |
| NEIGETOT | cm | Hauteur de neige totale au sol |
| HNEIGEFI3 | cm | Hauteur de neige fraiche tombee en 3h |
| HNEIGEFI1 | cm | Hauteur de neige fraiche tombee en 1h |
| TSNEIGE | °C et 1/10 | Temperature de surface de la neige |
| TUBENEIGE | cm | Enfoncement du tube de neige |
| ESNEIGE | code | Code descriptif de l'etat de la neige |
| CHARGENEIGE | kg/m2 | Charge de la neige |

### Rayonnement

| Champ | Unite | Description |
|-------|-------|-------------|
| GLO / GLO2 | J/cm2 | Rayonnement global horaire (UTC / TSV) |
| DIR / DIR2 | J/cm2 | Rayonnement direct horaire (UTC / TSV) |
| DIF / DIF2 | J/cm2 | Rayonnement diffus horaire (UTC / TSV) |
| UV / UV2 | J/cm2 | Rayonnement ultra-violet horaire (UTC / TSV) |
| UV_INDICE | 0-12 | Indice UV |
| INFRAR / INFRAR2 | J/cm2 | Rayonnement infra-rouge horaire (UTC / TSV) |
| INS / INS2 | mn | Insolation horaire (UTC / TSV) |

### Mer (semaphores)

| Champ | Unite | Description |
|-------|-------|-------------|
| VVMER | code 0-9 | Visibilite vers la mer |
| ETATMER | code 0-9 | Etat de la mer |
| DIRHOULE | rose de 360 | Direction de la houle |
| HVAGUE | m et 1/10 | Hauteur des vagues |
| PVAGUE | s et 1/10 | Periode des vagues |

---

## Glossaire

| Terme | Definition |
|-------|------------|
| **Abri meteorologique** | Enceinte ventilee protegeant le thermometre du rayonnement direct. Standard a 1.5m du sol. |
| **FU** | France Universelle = UTC + 1 heure (heure legale francaise hors heure d'ete). |
| **Octas** | Unite de mesure de la nebulosite. Le ciel est divise en 8 parties egales. |
| **Rose de 360** | Direction en degres, 0/360 = Nord, 90 = Est, 180 = Sud, 270 = Ouest. |
| **TSV** | Temps Solaire Vrai. Heure locale basee sur la position du soleil. |
| **UTC** | Temps Universel Coordonne. Heure de reference internationale. |

---

## References

### Documentation Meteo-France utilisee
- `../telechargement-climatologie-portail-api-meteofrance/docs/mf/observations/horaire.csv`
- `../telechargement-climatologie-portail-api-meteofrance/docs/mf/donnees-horaires/H_descriptif_champs.csv`
- `../telechargement-climatologie-portail-api-meteofrance/docs/mf/donnees-quotidiennes/Q_descriptif_champs_RR-T-Vent.csv`
- `../telechargement-climatologie-portail-api-meteofrance/docs/mf/donnees-quotidiennes/Q_descriptif_champs_autres-parametres.csv`

### Liens externes
- [Portail Donnees Publiques Meteo-France](https://donneespubliques.meteofrance.fr/)
- [Atlas international des nuages (OMM)](https://cloudatlas.wmo.int/fr/code-specifications-and-coding-procedures.html)
- [WMO Manuel des codes](https://library.wmo.int/idurl/4/35713)

---

*Document genere le 2 fevrier 2026 - Data For Good Saison 14*
*Verifie avec la documentation officielle Meteo-France*
