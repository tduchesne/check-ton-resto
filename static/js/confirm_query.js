function clearQueryError() {
    let error = document.getElementById("queryError");
    error.classList.remove("invalid-feedback");  
    error.style.display = "none"; 
}

function setQueryError(message) {
    let error = document.getElementById("queryError");
    error.classList.add("invalid-feedback");  
    error.innerHTML = message;
    error.style.display = "block";  
}

function checkSearchForm() {
    clearQueryError();
    var query = document.getElementById("query").value;
    if (query.length < 3) {
        setQueryError("La recherche doit contenir au moins 3 caractères.");
        return false;
    }
    return true;
}

document.getElementById("searchForm").addEventListener("submit", function(e) {
    let result = checkSearchForm();
    if (!result) {
        e.preventDefault();
        document.getElementById("query").classList.add("is-invalid");  
    } else {
        document.getElementById("query").classList.remove("is-invalid");
    }
});


