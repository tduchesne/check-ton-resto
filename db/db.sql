CREATE TABLE violations (
    id_poursuite INTEGER PRIMARY KEY,
    business_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    adresse TEXT NOT NULL,
    date_jugement TEXT NOT NULL,
    etablissement TEXT NOT NULL,
    montant INTEGER NOT NULL,
    proprietaire TEXT NOT NULL,
    ville TEXT NOT NULL,
    statut TEXT NOT NULL,
    date_statut TEXT NOT NULL,
    categorie TEXT NOT NULL
);