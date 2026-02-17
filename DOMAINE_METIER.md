# Documentation du Domaine Métier & Relations de Données
> "Comprendre le *Pourquoi* et le *Comment* derrière les données pour un Frontend intelligent."

Ce document complète le `FRONTEND_PLAN.md`. Il explique la logique métier sous-jacente et les relations entre les tables pour guider les décisions de design et d'UX, avec un accent particulier sur le contexte éducatif guinéen.

---

## 1. Vue d'Ensemble : "Modèle vs Instance"

Une distinction cruciale dans l'architecture est la séparation entre les **Données de Référence (Academic)** et les **Opérations Scolaires (School Operations)**.

*   **Academic (Le "Quoi")** : C'est le catalogue national/standard.
    *   Ex: "Année Académique 2024-2025", "Niveau 10ème Année", "Matière Mathématiques".
    *   Ces données sont globales et changent rarement.
*   **School Operations (Le "Comment" et "Où")** : C'est l'implémentation dans une école spécifique.
    *   Ex: "Lycée Filima - Année 2024-2025", "La classe de 10ème A du Lycée Filima".
    *   C'est ici que se passe la gestion réelle.

**Implication Frontend :**
*   Lors de la configuration d'une année scolaire (Wizard), l'utilisateur *sélectionne* des éléments académiques (ex: "Quels niveaux offrez-vous ?") pour créer ses propres structures (`SchoolYearLevel`).

---

## 2. Relations Clés & Hiérarchie

La structure de données suit une hiérarchie stricte qui doit se refléter dans la navigation (fil d'Ariane, sélecteurs de contexte).

### 2.1 La Chaîne de Configuration
```mermaid
graph TD
    School[School (L'École)] --> SchoolYear[SchoolYear (L'Année Scolaire)]
    SchoolYear --> SYCycle[SchoolYearCycle (Le Cycle: ex: Collège)]
    SYCycle --> SYLevel[SchoolYearLevel (Le Niveau: ex: 8ème Année)]
    SYLevel --> Classroom[Classroom (La Salle de Classe: ex: 8ème A)]
    
    SYLevel --> SYLevelSubject[LevelSubject (Le Programme: ex: Maths Coeff 2)]
```

*   **SchoolYear** : Partitionne toutes les données. Un élève est inscrit dans *une* année.
*   **SchoolYearLevel (SYL)** : C'est le niveau pédagogique dans cette école pour cette année.
*   **Classroom** : Subdivision physique/logique du niveau.
    *   *Règle métier* : Une classe appartient à un seul niveau. On ne mélange pas des élèves de 7ème et 8ème dans la même entité "Classroom" administrativement (même s'ils partagent une salle physique).

### 2.2 Inscriptions (Enrollment)
```mermaid
graph LR
    Student[User (Élève)] --> Enrollment[StudentEnrollment]
    Enrollment --> Classroom
    Classroom --> SYLevel[SchoolYearLevel]
```

*   **StudentEnrollment** : Le lien officiel. Il attache un élève à un niveau (`SchoolYearLevel`).
    *   *Statut* : Pré-inscrit, Actif, Suspendu, Transféré, Abandon.
    *   *Classroom* : Peut être nulle (ex: élève inscrit administrativement mais pas encore affecté à une classe).
    *   *Annual Identifier* : Le matricule unique pour cette année.

### 2.3 Pédagogie & Notes (Assessment)
C'est ici que le contexte guinéen est le plus fort.

```mermaid
graph TD
    Teacher --> Assignment[TeacherAssignment]
    Assignment --> Classroom
    Assignment --> Subject[SYLevelSubject]
    
    Assignment --> GradingSheet[Feuille de Notes]
    GradingSheet --> Assessment[Évaluation (Interro/Compo)]
    Assessment --> StudentAssessment[Note Élève]
```

*   **TeacherAssignment** : "Ce prof enseigne Maths en 10ème A". C'est la base de la sécurité (seul ce prof peut noter).
*   **SchoolYearLevelSubject** : Définit le **Coefficient**.
    *   *Contexte Guinéen* : Le coefficient est vital. Une note de 10/20 en Maths (Coeff 4) vaut 40 points, alors qu'en Histoire (Coeff 2) elle vaut 20 points. Le frontend doit toujours afficher les coefficients.

---

## 3. Spécificités du Contexte Guinéen (UX Tips)

### 3.1 Structure des Cycles
Le système guinéen est généralement structuré ainsi (à refléter dans les filtres par défaut) :
1.  **Primaire** : 1ère à 6ème Année (CEP).
2.  **Collège (Premier Cycle)** : 7ème à 10ème Année (BEPC/Brevet).
3.  **Lycée (Second Cycle)** : 11ème, 12ème, Terminale (BAC).
    *   *Important* : Au Lycée, il y a des **Options/Séries** (Sciences Mathématiques, Sciences Expérimentales, Sciences Sociales).
    *   *UX* : Les "Tracks" (séries) ne sont pertinents que pour le cycle Lycée.

### 3.2 Système d'Évaluation
*   **Périodes** : Semestres (Université) ou Trimestres (Scolaire classique). Le plus souvent **3 Trimestres**.
*   **Types de Notes** :
    *   **Interrogations / Devoirs** : Souvent coefficient faible ou faisant partie d'une "Moyenne de classe".
    *   **Compositions** : Examens de fin de trimestre, coefficient élevé (souvent double).
*   **Calcul de la Moyenne** : ((Moyenne Devoirs) + (Note Compo * 2)) / 3 est une formule classique, mais configurable.
*   **Mentions** : Tableau d'Honneur, Encouragements, Félicitations, Blâme.

### 3.3 Bulletins (Report Cards) & Relevés (Transcripts)
*   **Report Card (Bulletin)** : Par Période (Trimestre). Détaillé (Matière, Coeff, Note, Rang, Appréciation).
*   **Transcript (Relevé annuel)** : Résumé de l'année. Moyenne Annuelle = (T1 + T2 + T3) / 3. Décision de passage (Passe, Double, Réorienté).

---

## 4. Points d'Attention pour le Design Frontend

### 4.1 Sélecteurs de Contexte (Le "Global Header")
L'utilisateur travaille presque toujours dans un contexte précis.
*   **Selecteur d'Année** : Doit être visible partout. Par défaut = "Année Courante".
*   **Selecteur de Période (Trimestre)** : Pour les notes et bulletins.

### 4.2 États de l'Année (Workflow)
Une année scolaire a un cycle de vie qui impacte l'UI :
1.  **PLANNING** : On configure les classes, matières. *UI: Mode édition complet.*
2.  **ACTIVE** : Les élèves sont là, on note. *UI: Configuration structurelle (supprimer une matière) bloquée ou restreinte.*
3.  **ARCHIVED** : Année finie. *UI: Lecture seule stricte.*

### 4.3 Saisie des Notes (Data Grid)
C'est l'écran le plus utilisé par les profs.
*   **Performance** : Une classe peut avoir 50-80 élèves en Guinée (effectifs pléthoriques). La grille doit être légère.
*   **Navigation au clavier** : Vital pour saisir 60 notes à la suite.
*   **Sauvegarde** : Auto-save ou gros bouton "Enregistrer".

### 4.4 Gestion des Effectifs (Enrollment)
*   **Matricule** : Identifiant unique national ou école. Très utilisé pour la recherche.
*   **Photos** : Très important pour identifier les élèves dans les grandes classes.

## 5. Résumé Technique pour les Développeurs Frontend

| Concept Backend | Composition Frontend Suggérée | Pourquoi ? |
| :--- | :--- | :--- |
| `SchoolYear` | ContextProvider / Dropdown global | Tout est partitionné par année. |
| `Cycle/Level` | Cascading Dropdowns | On choisit le Cycle -> les Niveaux se mettent à jour. |
| `TeacherAssignment` | Permissions Guard | Si je ne suis pas assigné, je ne vois pas le bouton "Saisir Notes". |
| `StudentEnrollment` | "Card" Élève | Regroupe l'identité (User) et le statut scolaire (Classe). |
| `ReportCard` | Document / PDF View | C'est un "artefact" figé, pas juste une vue dynamique. |

---

*Ce document doit guider la création des composants et la logique de navigation dans l'application React/Next.js.*
