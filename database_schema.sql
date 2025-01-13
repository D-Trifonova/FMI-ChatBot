-- Drop the table if it exists
DROP TABLE IF EXISTS scraped_data;
DROP TABLE IF EXISTS search_queries;

-- Table to store scraped data
CREATE TABLE scraped_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_title TEXT NOT NULL,
    page_content TEXT NOT NULL,
    page_url TEXT NOT NULL
);

-- Table to store search queries
CREATE TABLE search_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    scraped_id INTEGER,
    FOREIGN KEY (scraped_id) REFERENCES scraped_data(id)
);
