# P2P_Synapse

Le projet **P2P_Synapsee** implémente un noeud de communication pour des réseaux en anneau interconnectés. Il permet à chaque noeud d'envoyer et de recevoir des messages pour la recherche de clés, la mise à jour de tables, et la gestion de réseaux. Ce système de nœuds utilise le **protocole WhiteBox** pour faciliter les opérations de recherche et de communication entre différents anneaux.

## Fonctionnalités

- **Connexion à des anneaux multiples** : chaque noeud peut rejoindre deux anneaux réseau, facilitant la redondance et la robustesse.
- **Recherche de clés** : possibilité de démarrer une recherche de clés dans les anneaux.
- **Gestion de messages de réseau** : prise en charge de messages `FIND`, `FOUND`, `NOT_FOUND`, `JOIN`, `READ_TABLE`, et `WRITE_TABLE`.

## Installation

### Prérequis

- Python 3.x
- Sockets Python (inclus dans les bibliothèques standard)
- `queue` et `threading` (inclus dans les bibliothèques standard)

### Perspectives

Connexions de plusieurs DHT Chords réels
