CREATE TABLE IF NOT EXISTS nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    language TEXT,
    tag TEXT
);

CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    relationship TEXT NOT NULL,
    FOREIGN KEY (source_id) REFERENCES nodes (id),
    FOREIGN KEY (target_id) REFERENCES nodes (id)
);
