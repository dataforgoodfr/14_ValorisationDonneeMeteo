## Conflit exemple

Pour creer un conflit , j'ai creer une branch A en modifiant le fichier .env.example.

Puis j'ai créé une branche B en modifiant également le fichier .env.example.

J'ai creer 2 pr , une pour la branche A et une pour la branche B.

j'ai merge la branch B sur main

et ducoup en actualisant la page de la PR de la branche A le conflit est apparu.

![alt text](<Capture d’écran du 2026-03-05 12-27-12.png>)

Donc la j'avais une branche avec un .env.example qui n'était pas à jour par rapport à la branche main.

Au moment de la pr j'ai donc résolu le conflit en laissant la main

![alt text](<Capture d’écran du 2026-03-05 12-28-34.png>)
