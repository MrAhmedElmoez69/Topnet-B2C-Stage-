#include <iostream>

int main()
{
    int categorieClient;
    double offre, debit;
    int engagementContractuel;
    double anciennete, suspension, montantEncours;
    int nombreReclamations;
    double delaiTraitementReclamation;
    int delaiMoyenPaiement;
    bool incidentPaiement, contentieux;

    std::cout << "Catégorie client (VIP: 1, Standard: 0): ";
    std::cin >> categorieClient;
    std::cout << "Offre (XDSL: 0.5, HD: 1): ";
    std::cin >> offre;
    std::cout << "Débit (100: 1, 50: 0.9, 30: 0.8, 20: 0.7, 12: 0.6, 10: 0.4, 8: 0.2, 4: 0): ";
    std::cin >> debit;
    std::cout << "Engagement contractuel (Période d'engagement: 0, Non engagé: 1): ";
    std::cin >> engagementContractuel;
    std::cout << "Ancienneté (en années): ";
    std::cin >> anciennete;
    std::cout << "Suspension (<2 fois par an: 1, >2 fois par an: 0): ";
    std::cin >> suspension;
    std::cout << "Montant de l'encours (<2 factures impayées: 1, Aucune facture: 0, Une facture: 0.5): ";
    std::cin >> montantEncours;
    std::cout << "Nombre de réclamations par an: ";
    std::cin >> nombreReclamations;
    std::cout << "Délai de traitement de réclamation (supérieur au délai théorique: 1, inférieur au délai théorique: 0): ";
    std::cin >> delaiTraitementReclamation;
    std::cout << "Délai moyen de paiement (en jours): ";
    std::cin >> delaiMoyenPaiement;
    std::cout << "Incident de paiement (OUI: 0, Non: 1): ";
    std::cin >> incidentPaiement;
    std::cout << "Contentieux (oui: 0, non: 1): ";
    std::cin >> contentieux;

    double poidsCategorieClient = 0.2;
    double poidsOffre = 0.3;
    double poidsDebit = 0.2;
    double poidsEngagementContractuel = 0.3;

    double scoreValeurCommerciale = (categorieClient * poidsCategorieClient) +
                                    (offre * poidsOffre) +
                                    (debit * poidsDebit) +
                                    (engagementContractuel * poidsEngagementContractuel);

    double poidsAnciennete = 0.2;
    double poidsSuspension = 0.5;
    double poidsMontantEncours = 0.3;

    double scoreEngagementClient = (anciennete * poidsAnciennete) +
                                   (suspension * poidsSuspension) +
                                   (montantEncours * poidsMontantEncours);

    double poidsNombreReclamations = 0.5;
    double poidsDelaiTraitementReclamation = 0.5;

    double scoreEngagementTOPNET = (nombreReclamations * poidsNombreReclamations) +
                                   (delaiTraitementReclamation * poidsDelaiTraitementReclamation);

    double poidsDelaiMoyenPaiement = 0.2;
    double poidsIncidentPaiement = 0.3;
    double poidsContentieux = 0.5;

    double scoreComportementClient = (delaiMoyenPaiement * poidsDelaiMoyenPaiement) +
                                     (incidentPaiement * poidsIncidentPaiement) +
                                     (contentieux * poidsContentieux);
    double scoreGlobalTotal = scoreValeurCommerciale +
                              scoreEngagementClient +
                              scoreEngagementTOPNET +
                              scoreComportementClient;

    if (scoreGlobalTotal <= 10.0)
    {
        int niveauRisque;
        if (scoreGlobalTotal >= 0 && scoreGlobalTotal <= 2.0)
        {
            niveauRisque = 4;
        }
        else if (scoreGlobalTotal >= 2.1 && scoreGlobalTotal <= 4.0)
        {
            niveauRisque = 3;
        }
        else if (scoreGlobalTotal >= 4.1 && scoreGlobalTotal <= 7.0)
        {
            niveauRisque = 2;
        }
        else if (scoreGlobalTotal >= 7.1 && scoreGlobalTotal <= 10)
        {
            niveauRisque = 1;
        }
        else
        {
            niveauRisque = -1; 
        }

        std::cout << "Score de la Valeur Commerciale: " << scoreValeurCommerciale << std::endl;
        std::cout << "Score d'Engagement Client: " << scoreEngagementClient << std::endl;
        std::cout << "Score d'Engagement TOPNET: " << scoreEngagementTOPNET << std::endl;
        std::cout << "Score de Comportement Client: " << scoreComportementClient << std::endl;
        std::cout << "Score global total: " << scoreGlobalTotal << std::endl;
        if (niveauRisque != -1)
        {
            std::cout << "Niveau de risque: " << niveauRisque << std::endl;
        }
        else
        {
            std::cout << "Erreur: impossible de déterminer le niveau de risque." << std::endl;
        }
    }

    return 0;
}
