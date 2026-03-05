# Résolution de conflit Git

## Ce qui s'est passé

1. **Dev A** (branche `feature/update-env`) a ajouté `leconflitdefou` en fin de fichier
2. **Dev B** (sur `main`) a ajouté `leconflitdemalade!!!` au même endroit

## Comment on a résolu

On a ouvert le fichier, on a vu les marqueurs de conflit :

```
<<<<<<< HEAD
leconflitdefou
=======
leconflitdemalade!!!
>>>>>>> main
```

On a décidé de **garder les deux textes**, un par ligne :

- Ligne 1 : le texte qui était déjà sur `main` (`leconflitdemalade!!!`)
- Ligne 2 : le texte de la feature branch (`leconflitdefou`)

Ensuite on a juste fait :

```bash
git add backend/.env.example
git rebase --continue
```

Et push de la branche.

## Résultat final

Le fichier contient maintenant les deux lignes, pas de perte de contenu.
