# TheHive + Cortex — SOC Case Management & Enrichissement IoC
### Investigation complète d'un incident de phishing, de la détection à la clôture

![Stack](https://img.shields.io/badge/stack-TheHive%203.5.1%20%7C%20Cortex%203.1.7-FFD93D)
![Deploy](https://img.shields.io/badge/d%C3%A9ploiement-Docker%20Compose-2496ED?logo=docker&logoColor=white)
![Scope](https://img.shields.io/badge/scope-Case%20Management%20%7C%20IoC%20Enrichment-B8860B)
![Verdict](https://img.shields.io/badge/verdict-COMPROMIS-B83A3A)
![MTTR](https://img.shields.io/badge/MTTR-16%20min-3B7D4F)

Déploiement et exploitation de **TheHive** (gestion des cas d'incident) et **Cortex** (moteur d'enrichissement des indicateurs de compromission), intégrés via API, pour mener de bout en bout l'investigation d'un incident simulé : une campagne de phishing avec exfiltration de données.

> Auteurs : **Wissal MOKDAD** et **Hafssa AZARG** — EMSI, 27 mars 2026

---

## Table des matières
1. [Contexte](#contexte)
2. [Présentation des outils](#présentation-des-outils)
3. [Architecture](#architecture)
4. [Déploiement Docker](#déploiement-docker)
5. [Connexion Cortex ↔ TheHive](#connexion-cortex--thehive)
6. [Création du cas d'incident](#création-du-cas-dincident)
7. [Observables et tâches](#observables-et-tâches)
8. [Enrichissement IoC via Cortex](#enrichissement-ioc-via-cortex)
9. [Corrélation et verdict](#corrélation-et-verdict)
10. [Timeline et remédiation](#timeline-et-remédiation)
11. [Documentation](#documentation)

---

## Contexte

Un SOC doit détecter, analyser et répondre aux incidents en temps réel, tout en coordonnant plusieurs analystes et en documentant chaque étape. **TheHive** et **Cortex**, deux outils open source, structurent et automatisent ce processus : TheHive centralise la gestion du cas, Cortex automatise l'enrichissement des indicateurs de compromission (IoC) via des dizaines d'analyseurs.

**Scénario simulé** : `CAS-0042 — Suspicious IP Activity`, classifié **TLP:AMBER**, impliquant une adresse IP suspecte, un domaine frauduleux et un fichier malveillant détecté sur un poste compromis.

## Présentation des outils

| Outil | Rôle |
|---|---|
| **TheHive** | Création de cas (titre, sévérité, TLP, tags), ajout d'observables, création et suivi de tâches |
| **Cortex** | Soumission des observables à des analyseurs spécialisés (WHOIS, hash lookup, réputation IP...) |
| **Intégration** | Depuis TheHive, un observable est envoyé à Cortex en un clic ; les résultats reviennent directement dans le cas |

## Architecture

![Architecture de la stack](diagrams/01-architecture-stack.png)

| Composant | Version | Port | Rôle |
|---|---|---|---|
| TheHive | 3.5.1 | 9000 | Plateforme centrale de gestion des incidents |
| Cortex | 3.1.7 | 9001 | Moteur d'analyse et d'enrichissement des IoC |
| Elasticsearch | 7.9.3 | 9200 | Stockage et indexation |
| Cassandra | — | — | Persistance des données TheHive |

## Déploiement Docker

Déployé sur une VM Linux Ubuntu 22.04, en une seule commande :

```bash
docker-compose up -d
```

| `docker-compose up` | Conteneurs actifs (`docker ps`) |
|:--:|:--:|
| ![docker-compose up](screenshots/01-docker-compose-up.png) | ![docker ps](screenshots/02-docker-ps-containers.png) |

Une erreur `TLS handshake timeout` est survenue au premier `pull` (latence réseau) ; `docker-compose up -d` a ensuite démarré les quatre services avec succès.

À la première ouverture, TheHive demande la création d'un compte administrateur :

![Création du compte admin](screenshots/03-thehive-admin-account.png)

| Connexion TheHive (`:9000`) | Connexion Cortex (`:9001`) |
|:--:|:--:|
| ![Login TheHive](screenshots/04-thehive-login.png) | ![Login Cortex](screenshots/06-cortex-login.png) |

| Liste des cas (TheHive) | Organisations (Cortex) |
|:--:|:--:|
| ![Cases TheHive](screenshots/05-thehive-cases-list.png) | ![Organizations Cortex](screenshots/07-cortex-organizations.png) |

## Connexion Cortex ↔ TheHive

1. Génération d'une **clé API** dans Cortex (menu *Users*).
2. Configuration dans TheHive (`thehive.conf`) : URL `http://cortex:9001` + clé API.
3. Test de connexion validé, intégration opérationnelle.
4. Activation des analyseurs : **WHOIS Lookup**, **Hash Lookup**, **Cyberprotect_ThreatScore_3_0**.

| Clé API générée dans Cortex | Connecteur Cortex dans `thehive.conf` |
|:--:|:--:|
| ![API Key Cortex](screenshots/08-cortex-users-api-key.png) | ![thehive.conf](screenshots/09-thehive-conf-cortex-connector.png) |

## Création du cas d'incident

| Paramètre | Valeur |
|---|---|
| Titre | Suspicious IP Activity |
| Sévérité | High |
| TLP | Amber |
| Tags | malware, investigation |
| Description | Activité réseau suspecte, connexions inhabituelles, investigation Cortex recommandée |

| Création du cas | Détails du cas créé |
|:--:|:--:|
| ![Create case](screenshots/10-create-new-case.png) | ![Case details](screenshots/11-case-details.png) |

## Observables et tâches

Trois observables ajoutés au cas :

| Type | Valeur | Tags |
|---|---|---|
| Domaine | `update-microsoft.ru` | malware, suspicious, network, phishing |
| Adresse IP | `185.220.101.47` | malware, suspicious, network, phishing |
| Hash MD5 | fichier suspect téléchargé | malware, file, critical |

| Observable domaine | Observable IP | Observable hash |
|:--:|:--:|:--:|
| ![Domaine](screenshots/12-observable-domain.png) | ![IP](screenshots/13-observable-ip.png) | ![Hash](screenshots/14-observable-hash.png) |

Trois tâches structurent l'investigation : **analyse de l'IP**, **analyse du domaine**, **vérification du hash**.

![Liste des tâches](screenshots/15-tasks-list.png)

## Enrichissement IoC via Cortex

Cortex embarque jusqu'à 260 analyseurs ; trois ont été activés et utilisés pour ce cas.

| Liste des analyseurs (CLI) | 260 analyseurs disponibles (admin) |
|:--:|:--:|
| ![Analyzers CLI](screenshots/16-cortex-analyzers-cli-list.png) | ![260 analyzers](screenshots/17-cortex-analyzers-admin-260.png) |

### Lancement des analyses depuis TheHive

![Run selected analyzers](screenshots/18-run-selected-analyzers.png)

| Analyseur | Observable | Résultat |
|---|---|---|
| **WHOIS Lookup** | `update-microsoft.ru` | Domaine créé en nov. 2024, confidentialité Panama, pointe vers `185.220.101.47`, pas de DNSSEC → **MALVEILLANT** |
| **Hash Lookup (MalwareBazaar)** | fichier suspect | **AgentTesla Stealer**, détecté par 62/70 moteurs AV, usurpe une mise à jour Windows → **MALVEILLANT** |
| **Cyberprotect_ThreatScore_3_0** | 2 hashs + IP interne `192.168.19.129` | Corrélation confirmée avec le poste compromis → **COMPROMIS** |

## Corrélation et verdict

![Corrélation des IoC](diagrams/03-correlation-ioc.png)

Le domaine pointe vers l'IP, le malware communique avec cette même IP, et le nom du fichier imite une mise à jour Windows pour tromper la victime : les trois observables appartiennent à **une seule infrastructure d'attaque coordonnée**.

## Timeline et remédiation

![Timeline de l'incident](diagrams/04-timeline-incident.png)

| Historique des analyses Cortex (Jobs History) | Infrastructure Docker Desktop |
|:--:|:--:|
| ![Jobs History](screenshots/19-jobs-history-timeline.png) | ![Docker Desktop](screenshots/20-docker-desktop-containers.png) |

**Verdict final** : vrai positif. Poste `WKSTN-07` compromis par le malware AgentTesla Stealer, infrastructure C2 corrélée avec le domaine et l'IP du cas.

**Actions de remédiation :**
- Isolation du poste compromis
- Blocage des hashs malveillants
- Réinitialisation des identifiants (credentials)
- Export des IoC vers MISP

**MTTR : 16 minutes** — incident contenu et clôturé.

## Documentation

- Rapport complet : [`docs/Rapport-TheHive-Cortex.pdf`](docs/Rapport-TheHive-Cortex.pdf)

---

*Investigation réalisée dans un cadre pédagogique, sur un environnement Docker isolé et un incident simulé.*
