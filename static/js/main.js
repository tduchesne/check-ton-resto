// Script pour index.html 
document.addEventListener('DOMContentLoaded', function() {

    const searchForm = document.getElementById("searchForm");
    const queryInput = document.getElementById("query");
    const queryError = document.getElementById("queryError");

    /**
     * Efface le message d'erreur de la recherche.
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
     * Affiche un message d'erreur de recherche.
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
     * Vérifie le formulaire de recherche.
     * @returns {boolean} - Retourne true si le formulaire est valide, sinon false.
     */
    function checkSearchForm() {
        clearQueryError();
        if (queryInput && queryInput.value.length < 3) {
            setQueryError("La recherche doit contenir au moins 3 caractères.");
            return false;
        }
        return true;
    }

    if (searchForm) {
        searchForm.addEventListener("submit", function(e) {
            if (!checkSearchForm()) {
                e.preventDefault(); 
            }
        });
        if (queryInput) {
            queryInput.addEventListener('input', clearQueryError);
        }
    }

    const dateSearchForm = document.getElementById('date-search-form');
    const resultsContainer = document.getElementById('quick-search-results');
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end-date');
    const dateError = document.getElementById('dateError');

    /**
     * Efface le message d'erreur de date.
     */
    function clearDateError() {
        if (dateError) {
            dateError.style.display = "none";
            dateError.textContent = "";
        }
        if (startDateInput) startDateInput.classList.remove("is-invalid");
        if (endDateInput) endDateInput.classList.remove("is-invalid");
    }

    /*
    * Affiche un message d'erreur de date.
    * @param {string} message - Le message d'erreur à afficher.
    * @param {HTMLElement|null} invalidInput - L'élément d'entrée invalide (ou un tableau d'éléments).
    * Si null, aucune classe d'erreur n'est ajoutée.
    */ 
    function setDateError(message, invalidInput = null) {
        if (dateError) {
            dateError.textContent = message;
            dateError.style.display = "block";
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
     * Vérifie le formulaire de date.
     * @returns {boolean} - Retourne true si le formulaire est valide, sinon false.
     */
    function checkDateForm() {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        if (!startDate) {
            setDateError("Veuillez sélectionner une date de début.", startDateInput);
            return false;
        }
        if (!endDate) {
            setDateError("Veuillez sélectionner une date de fin.", endDateInput);
            return false;
        }
        const startDateObj = new Date(startDate);
        const endDateObj = new Date(endDate);
        if (startDateObj > endDateObj) {
             setDateError("La date de début ne peut pas être après la date de fin.", [startDateInput, endDateInput]);
            return false;
        }
        return true; 
    }

    if (dateSearchForm) {
        dateSearchForm.addEventListener('submit', async function(event) {
            event.preventDefault(); 

            
            clearDateError();
            resultsContainer.innerHTML = '';

            // Vérifie si le formulaire de date est valide avant de soumettre
            if (checkDateForm()) {
                resultsContainer.innerHTML = '<p>Chargement des résultats...</p>';
                const startDate = startDateInput.value;
                const endDate = endDateInput.value;
                const apiUrl = `/contrevenants?du=${startDate}&au=${endDate}`;
            
            try {
                const response = await fetch(apiUrl);

                if (!response.ok) {
                    throw new Error(`Erreur HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                displayResultsTable(data);

            } catch (error) {
                console.error('Erreur lors de la recherche par date:', error);
                resultsContainer.innerHTML = `<p class="error">Erreur: ${error.message}</p>`;
            }
            }
            
        });

        
        if (startDateInput) {
            startDateInput.addEventListener('change', clearDateError);
        }
        if (endDateInput) {
            endDateInput.addEventListener('change', clearDateError);
        }
    }

    /**
     * Affiche les résultats des contraventions dans un tableau.
     * @param {Array} violations - Le tableau des objets de contravention reçus de l'API.
     */
    function displayResultsTable(violations) {
        // Vérifie s'il y a des violations
        if (!violations || violations.length === 0) {
            resultsContainer.innerHTML = '<p>Aucune contravention trouvée pour cette période.</p>';
            return;
        }

        // Compte le nombre de contraventions par établissement
        const establishmentCounts = {}; 
        
        for (const violation of violations) {
            const establishment = violation.etablissement || 'Établissement non spécifié';

            if (establishmentCounts.hasOwnProperty(establishment)) {
                establishmentCounts[establishment]++;
            } else {
                establishmentCounts[establishment] = 1;
            }
        }

        // Trie les établissements par nom
        const establishmentNames = Object.keys(establishmentCounts);
        establishmentNames.sort((a, b) => a.localeCompare(b)); 

        // Crée le tableau HTML
        let tableHTML = `
            <h3>Résultats (${establishmentNames.length} établissements trouvés)</h3>
            <table border="1">
                <thead>
                    <tr>
                        <th>Établissement</th>
                        <th>Nombre de contraventions</th>
                    </tr>
                </thead>
                <tbody>
        `;

        for (const establishmentName of establishmentNames) {
            const count = establishmentCounts[establishmentName];

            tableHTML += `
                <tr>
                    <td>${escapeHTML(establishmentName)}</td>
                    <td>${count}</td>
                </tr>
            `;
        }

        tableHTML += `
                </tbody>
            </table>
        `;

        resultsContainer.innerHTML = tableHTML;
    }

    /**
     * Échappe les caractères HTML potentiellement dangereux dans une chaîne 
     * pour prévenir les attaques XSS (Cross-Site Scripting) lors de l'insertion 
     * de cette chaîne dans le DOM.
     * @param {string} str - La chaîne à échapper.
     * @returns {string} La chaîne échappée.
     */
    function escapeHTML(str) {
        if (typeof str !== 'string') return str; 
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(str));
        return div.innerHTML;
    }

}); 