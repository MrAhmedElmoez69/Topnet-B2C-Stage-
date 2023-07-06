# Définition des poids pour chaque axe
poids_valeur_commerciale = 0.2
poids_engagement_client = 0.2
poids_engagement_TOPNET = 0.1
poids_comportement_client = 0.5

# Saisie des données de chaque axe
categorie_client = input("Catégorie client (VIP/Standard): ")
offre = input("Offre (XDSL/HD): ")
debit = int(input("Débit (100/50/30/20/12/10/8/4): "))
engagement_contractuel = input("Engagement contractuel (Période d'engagement/Non engagé): ")
anciennete = input("Ancienneté (2 ans et plus/1 an < a < 2 ans/< 1 an): ")
suspension = input("Suspension (< 2 fois par an/> 2 fois par an): ")
montant_encours = input("Montant de l'encours (< 2 factures impayées/Aucune facture/Une facture): ")
nombre_reclamations = input("Nombre de réclamations par an (Nombre de réclamations par an > 4/2 < nombre de réclamations par an < 4/Nombre de réclamations par an < 2): ")
delai_traitement_reclamation = input("Délai de traitement de réclamation (Délai théorique de traitement de réclamation/ < Délai théorique de traitement de réclamation): ")
delai_moyen_paiement = input("Délai moyen de paiement (< 30 jours/ > 30 jours): ")
incident_paiement = input("Incident de paiement (OUI/Non): ")
contentieux = input("Contentieux (Oui/Non): ")

# Calcul du score global en multipliant chaque valeur par son poids
score_valeur_commerciale = 0
if categorie_client == "VIP":
    score_valeur_commerciale += 1 * poids_valeur_commerciale

if offre == "HD":
    score_valeur_commerciale += 1 * poids_valeur_commerciale
elif offre == "XDSL":
    score_valeur_commerciale += 0.5 * poids_valeur_commerciale

score_engagement_client = 0
if anciennete == "2 ans et plus":
    score_engagement_client += 1 * poids_engagement_client
elif anciennete == "1 an < a < 2 ans":
    score_engagement_client += 0.5 * poids_engagement_client

if suspension == "< 2 fois par an":
    score_engagement_client += 1 * poids_engagement_client

if montant_encours == "< 2 factures impayées":
    score_engagement_client += 1 * poids_engagement_client
elif montant_encours == "Aucune facture":
    score_engagement_client += 0 * poids_engagement_client
elif montant_encours == "Une facture":
    score_engagement_client += 0.5 * poids_engagement_client

score_engagement_TOPNET = 0
if nombre_reclamations == "Nombre de réclamations par an > 4":
    score_engagement_TOPNET += 1 * poids_engagement_TOPNET
elif nombre_reclamations == "2 < nombre de réclamations par an < 4":
    score_engagementpar  += 0.5 * poids_engagement_TOPNET

if delai_traitement_reclamation == "Délai théorique de traitement de réclamation":
    score_engagement_TOPNET += 1 * poids_engagement_TOPNET

score_comportement_client = 0
if delai_moyen_paiement == "< 30 jours":
    score_comportement_client += 1 * poids_comportement_client

if incident_paiement == "Non":
    score_comportement_client += 1 * poids_comportement_client

if contentieux == "Non":
    score_comportement_client += 1 * poids_comportement_client

# Calcul du score global en pourcentage
score_global = (score_valeur_commerciale + score_engagement_client + score_engagement_TOPNET + score_comportement_client) * 100

# Affichage du score global
print("Score Global: {}%".format(score_global))
