document.addEventListener('DOMContentLoaded', function() {

    // Gestionnaire de recherche générique 
    const genericSearchForm = document.getElementById("searchForm");
    const queryInput = document.getElementById("query");
    const queryError = document.getElementById("queryError");

    /**
     * Efface le message d'erreur de la recherche générique.
     */
    function clearQueryError() {
        if (queryError) {
            queryError.style.display = "none";
            queryError.textContent = "";
        }
        if (queryInput) {
             queryInput.classList.remove("is-invalid");
        }
    }

    /**
     * Affiche un message d'erreur de recherche générique.
     * @param {string} message - Le message d'erreur à afficher.
     */
    function setQueryError(message) {
        if (queryError) {
            queryError.textContent = message;
            queryError.style.display = "block";
        }
         if (queryInput) {
             queryInput.classList.add("is-invalid");
         }
    }

    /**
     * Vérifie le formulaire de recherche générique.
     * @returns {boolean} - Retourne true si le formulaire est valide, sinon false.
     */
    function checkGenericSearchForm() {
        clearQueryError();
        if (queryInput && queryInput.value.length < 3) {
            setQueryError("La recherche doit contenir au moins 3 caractères.");
            return false;
        }
        return true;
    }

    if (genericSearchForm) {
        genericSearchForm.addEventListener("submit", function(e) {
            // Empêche la soumission seulement si invalide (pour la recherche classique)
            if (!checkGenericSearchForm()) {
                e.preventDefault();
            }
            // Si valide, la soumission classique (rechargement) se produit.
        });
        // Efface l'erreur de validation si l'utilisateur change la valeur
        if (queryInput) {
            queryInput.addEventListener('input', clearQueryError);
        }
    }

    // Gestionnaire de recherche par date 
    const dateSearchForm = document.getElementById('date-search-form');
    const resultsDisplayArea = document.getElementById('quick-search-results');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const dateValidationErrorElement = document.getElementById('dateError');

    // Stockage des dernières données du résumé et des dates utilisées
    let lastSummaryData = null;
    let lastSearchStartDate = null;
    let lastSearchEndDate = null;

    /**
     * Efface le message d'erreur de validation des dates.
     */
    function clearDateValidationError() {
        if (dateValidationErrorElement) {
            dateValidationErrorElement.style.display = "none";
            dateValidationErrorElement.textContent = "";
        }
        if (startDateInput) startDateInput.classList.remove("is-invalid");
        if (endDateInput) endDateInput.classList.remove("is-invalid");
    }

    /**
     * Affiche un message d'erreur de validation des dates.
     * @param {string} message - Le message d'erreur.
     * @param {HTMLElement|Array<HTMLElement>|null} invalidInput - L'élément (ou les éléments) à marquer comme invalide(s).
     */
    function setDateValidationError(message, invalidInput = null) {
        if (dateValidationErrorElement) {
            dateValidationErrorElement.textContent = message;
            dateValidationErrorElement.style.display = "block";
        }
        if (invalidInput) {
            if (Array.isArray(invalidInput)) {
                invalidInput.forEach(input => input && input.classList.add("is-invalid"));
            } else if (invalidInput) {
                invalidInput.classList.add("is-invalid");
            }
        }
    }

    /**
     * Vérifie la validité du formulaire de recherche par date.
     * @returns {boolean} True si valide, False sinon.
     */
    function checkDateSearchForm() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        if (!startDate) {
            setDateValidationError("Veuillez sélectionner une date de début.", startDateInput);
            return false;
        }
        if (!endDate) {
            setDateValidationError("Veuillez sélectionner une date de fin.", endDateInput);
            return false;
        }
        const startDateObj = new Date(startDate);
        const endDateObj = new Date(endDate);
        if (startDateObj > endDateObj) {
            setDateValidationError("La date de début ne peut pas être après la date de fin.", [startDateInput, endDateInput]);
            return false;
        }
        return true;
    }

    // Écouteur pour le formulaire de recherche par date
    if (dateSearchForm) {
        dateSearchForm.addEventListener('submit', async function(event) {
            event.preventDefault(); 

            // Efface l'erreur de validation et la zone de résultats
            clearDateValidationError();
            resultsDisplayArea.innerHTML = ''; 

            if (checkDateSearchForm()) { 
                resultsDisplayArea.innerHTML = '<p>Chargement du résumé des contraventions...</p>';
                const startDate = startDateInput.value;
                const endDate = endDateInput.value;
                const apiUrlSummary = `/contrevenants?du=${startDate}&au=${endDate}`;

                try {
                    const response = await fetch(apiUrlSummary);
                    if (!response.ok) {
                        let errorMsg = `Erreur HTTP ${response.status}`;
                        try { errorMsg = (await response.json()).error || errorMsg; } catch (e) { /* ignore json parsing error */}
                        throw new Error(errorMsg);
                    }
                    const summaryData = await response.json();

                    // Stocke les données et les dates pour pouvoir revenir au résumé
                    lastSummaryData = summaryData;
                    lastSearchStartDate = startDate;
                    lastSearchEndDate = endDate;

                    // Affiche le tableau résumé
                    displaySummaryTable(summaryData);

                } catch (error) {
                    console.error('Erreur lors de la recherche par date:', error);
                    resultsDisplayArea.innerHTML = `<p class="error">Erreur lors de la récupération du résumé: ${error.message}</p>`;
                    // Efface les données stockées en cas d'erreur
                    lastSummaryData = null;
                    lastSearchStartDate = null;
                    lastSearchEndDate = null;
                }
            }
        });

        // Efface l'erreur de validation si l'utilisateur change une date
        if (startDateInput) startDateInput.addEventListener('change', clearDateValidationError);
        if (endDateInput) endDateInput.addEventListener('change', clearDateValidationError);
    }

    /**
     * Affiche le tableau résumé (établissements + compte) basé sur la recherche par date.
     * Rend les noms d'établissements cliquables pour afficher les détails.
     * @param {Array} summaryViolations - Le tableau des objets de contravention reçus de l'API /contrevenants.
     */
    function displaySummaryTable(summaryViolations) {
         // Stocke ou met à jour les données pour le bouton retour
         lastSummaryData = summaryViolations;
         // Vérification de sécurité pour les dates 
         if (!lastSearchStartDate || !lastSearchEndDate) {
             console.error("Dates de recherche manquantes lors de l'affichage du résumé.");
             resultsDisplayArea.innerHTML = '<p>Erreur interne: Impossible d\'afficher le résumé sans période définie.</p>';
             return;
         }
        if (!summaryViolations || summaryViolations.length === 0) {
            resultsDisplayArea.innerHTML = `<p>Aucune contravention trouvée pour la période du ${lastSearchStartDate} au ${lastSearchEndDate}.</p>`;
            return;
        }

        // Compte les occurrences par établissement
        const establishmentCounts = {};
        for (const violation of summaryViolations) {
            const establishment = violation.etablissement || 'Établissement non spécifié';
            establishmentCounts[establishment] = (establishmentCounts[establishment] || 0) + 1;
        }
        const establishmentNames = Object.keys(establishmentCounts).sort((a, b) => a.localeCompare(b));

        // Construit le tableau HTML du résumé
        let tableHTML = `
            <h3>${establishmentNames.length} établissements trouvés</h3>
            <div class="table-container border rounded">
            <table class="table table-striped table-hover table-sm mb-0">
                <thead>
                    <tr>
                        <th>Établissement (Cliquez pour détails)</th>
                        <th>Nombre de contraventions</th>
                    </tr>
                </thead>
                <tbody>
        `;
        for (const establishmentName of establishmentNames) {
            const count = establishmentCounts[establishmentName];
            // Bouton pour voir les détails
            tableHTML += `
                <tr>
                    <td>
                        <button type="button" class="btn btn-link p-0 view-infraction-details" data-name="${escapeHTML(establishmentName)}">
                            ${escapeHTML(establishmentName)}
                        </button>
                    </td>
                    <td>${count}</td>
                </tr>
            `;
        }
        tableHTML += `</tbody></table></div>`;
        resultsDisplayArea.innerHTML = tableHTML;
    }

    // Gestionnaire d'événements pour les clics dans la zone de résultats 
    if (resultsDisplayArea) {
        resultsDisplayArea.addEventListener('click', async function(event) {

            // Clic pour voir les détails d'un établissement 
            const detailButton = event.target.closest('.view-infraction-details');
            if (detailButton) {
                event.preventDefault();
                const establishmentName = detailButton.dataset.name;

                if (!lastSearchStartDate || !lastSearchEndDate) {
                    console.error("Dates de recherche non disponibles pour afficher les détails.");
                    resultsDisplayArea.innerHTML = '<p class="error">Erreur: Veuillez d\'abord effectuer une recherche par date valide.</p>';
                    return;
                }
                // Sauvegarde la position de défilement actuelle pour revenir à cette position après le rendu du tableau 
                const savedScrollY = window.scrollY; 

                resultsDisplayArea.innerHTML = '<p>Chargement des détails des infractions...</p>';
                const encodedName = encodeURIComponent(establishmentName);
                const apiUrlDetails = `/infractions/${encodedName}?du=${lastSearchStartDate}&au=${lastSearchEndDate}`;

                try {
                    const response = await fetch(apiUrlDetails);
                    if (!response.ok) {
                        let errorMsg = `Erreur HTTP ${response.status}`;
                        try { errorMsg = (await response.json()).error || errorMsg; } catch (e) {}
                        throw new Error(errorMsg);
                    }
                    const detailedInfractions = await response.json();

                    // Affiche le tableau détaillé 
                    displayInfractionDetailsTable(detailedInfractions, lastSearchStartDate, lastSearchEndDate);
                    // Restaure la position de défilement
                    requestAnimationFrame(() => {
                        window.scrollTo(0, savedScrollY);
                    });

                } catch (error) {
                    console.error("Erreur lors de la récupération des détails d'infraction:", error);
                    resultsDisplayArea.innerHTML = `<p class="error">Erreur lors du chargement des détails: ${error.message}</p>`;
                    requestAnimationFrame(() => {
                        window.scrollTo(0, savedScrollY);
                    });
                }
            }

            //  Clic pour revenir au tableau résumé 
            const backButton = event.target.closest('.back-to-summary');
            if (backButton) {
                event.preventDefault();
                if (lastSummaryData && lastSearchStartDate && lastSearchEndDate) { 
                    // Réaffiche le tableau résumé en utilisant les données stockées
                    displaySummaryTable(lastSummaryData);
                } else {
                    resultsDisplayArea.innerHTML = '<p>Erreur : Données du résumé non disponibles. Veuillez relancer une recherche par date.</p>';
                }
            }
        });
    }

    /**
     * Formate une chaîne de date 'YYYYMMDD' en 'YYYY-MM-DD'.
     * Retourne la chaîne originale ou 'N/A' si invalide.
     * @param {string} dateStr - La chaîne de date au format 'YYYYMMDD'.
     * @returns {string} La date formatée ou la chaîne originale ou N/A.
     */
    function formatDateString(dateStr) {
        if (!dateStr || typeof dateStr !== 'string' || dateStr.length !== 8 || !/^\d{8}$/.test(dateStr)) {
            return dateStr || 'N/A';
        }
        try {
            const year = dateStr.substring(0, 4);
            const month = dateStr.substring(4, 6);
            const day = dateStr.substring(6, 8);
            return `${year}-${month}-${day}`;
        } catch (e) {
            console.error("Erreur de formatage de date pour:", dateStr, e);
            return dateStr; 
        }
    }

    /**
     * Affiche le tableau détaillé des infractions pour un établissement donné dans une période.
     * Inclut un bouton "Retour" pour revenir au résumé.
     * @param {Array} infractions - Tableau d'objets d'infraction détaillés.
     * @param {string} startDate - Date de début de la période (pour le titre).
     * @param {string} endDate - Date de fin de la période (pour le titre).
     */
    function displayInfractionDetailsTable(infractions, startDate, endDate) {
        // Le bouton "Retour"
        let backButtonHTML = `
            <button type="button" class="btn btn-secondary btn-sm mb-3 back-to-summary">
                Retour
            </button>
        `;

        if (!infractions || infractions.length === 0) {
            // Affiche bouton retour + message "pas de détails"
            resultsDisplayArea.innerHTML = backButtonHTML + `<p>Aucune infraction détaillée trouvée pour cet établissement durant la période du ${startDate} au ${endDate}.</p>`;
            return;
        }

        // Construit le tableau détaillé HTML
        let tableHTML = `
            <h4>Détails des infractions pour ${escapeHTML(infractions[0].etablissement)}</h4>
            <div class="table-responsive border rounded">
                <table class="table table-striped table-bordered table-sm mb-0">
                     <thead>
                         <tr>
                             <th>Date Infraction</th>
                             <th>Description</th>
                             <th>Adresse</th>
                             <th>Date Jugement</th>
                             <th>Montant</th>
                             <th>Propriétaire</th>
                             <th>Ville</th>
                             <th>Statut</th>
                             <th>Date Statut</th>
                             <th>Catégorie</th>
                         </tr>
                     </thead>
                     <tbody>
        `;
        for (const infraction of infractions) {
            // Génère chaque ligne du tableau détaillé
             tableHTML += `
                 <tr>
                     <td>${formatDateString(infraction.date)}</td>
                     <td>${escapeHTML(infraction.description)}</td>
                     <td>${escapeHTML(infraction.adresse)}</td>
                     <td>${formatDateString(infraction.date_jugement)}</td>
                     <td>${escapeHTML(infraction.montant)}$</td>
                     <td>${escapeHTML(infraction.proprietaire)}</td>
                     <td>${escapeHTML(infraction.ville)}</td>
                     <td>${escapeHTML(infraction.statut)}</td>
                     <td>${formatDateString(infraction.date_statut)}</td>
                     <td>${escapeHTML(infraction.categorie)}</td>
                 </tr>
             `;
        }
        tableHTML += `</tbody></table></div>`;

        // Affiche le bouton Retour suivi du tableau détaillé
        resultsDisplayArea.innerHTML = backButtonHTML + tableHTML;
    }

    /**
     * Utilitaire pour échapper les caractères HTML.
     * @param {string} str - La chaîne à échapper.
     * @returns {string} La chaîne échappée.
     */
    function escapeHTML(str) {
        // Si l'entrée n'est pas une chaîne, on la retourne telle quelle pour éviter une erreur
        if (typeof str !== 'string') return str;
        // Crée un élément temporaire
        const div = document.createElement('div');
        // Définit son contenu texte (méthode sûre contre XSS)
        div.textContent = str;
        // Lit le innerHTML, qui contiendra les entités échappées
        return div.innerHTML;
    }

}); 