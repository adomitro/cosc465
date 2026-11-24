--.mode box
PRAGMA foreign_keys = ON;

--Use this file to start up the database structure
--Just in case. Running this file WILL delete all preexisting data
DROP TABLE IF EXISTS fonts;
DROP TABLE IF EXISTS languages;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS names;
DROP TABLE IF EXISTS filters;
DROP TABLE IF EXISTS language_filters;
DROP VIEW IF EXISTS filters_by_lang;
DROP INDEX IF EXISTS idx_words_meaning;

--Create tables

-- Stores file paths to images of different scripts
CREATE TABLE fonts (
    font_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    file_path TEXT
);

-- Stores info for each conlang that will be used to generate new words in it
CREATE TABLE languages (
    language_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    phonemes TEXT NOT NULL,
    vowels TEXT,
    clusters TEXT,
    font_id INTEGER,
    FOREIGN KEY (font_id)
        REFERENCES fonts(font_id)
);

-- Stores all words that have been inputted into the database so far
CREATE TABLE words (
    word_id INTEGER PRIMARY KEY,
    word TEXT NOT NULL,
    meaning TEXT NOT NULL,
    pronunciation TEXT,
    language_id INTEGER,
    FOREIGN KEY (language_id)
        REFERENCES languages(language_id)
);

-- Stores all names that have been inputted into the database so far
CREATE TABLE names (
    name_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    type TEXT NOT NULL,
    notes TEXT,
    language_id INTEGER,
    FOREIGN KEY (language_id)
        REFERENCES languages(language_id)
);

-- stores filters and rules that are used for word creation
CREATE TABLE filters (
    filter_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    filter_rule TEXT NOT NULL
);

-- junction table linking filters to the languages that use them
CREATE TABLE language_filters (
    filter_id INTEGER,
    language_id INTEGER,
    filter_value INTEGER, -- Specific value used in a language's version of a filter, such as vowel_limit(klingon) = 2
    is_active BOOLEAN, -- Is this filter currently in use for the generator? Toggled often

    FOREIGN KEY (filter_id)
        REFERENCES filters(filter_id),
    FOREIGN KEY (language_id)
        REFERENCES languages(language_id),
    PRIMARY KEY (language_id, filter_id)
);

-- CREATE VIEW: the human readable version of the language_filters table that will be shown to the user
CREATE VIEW filters_by_lang AS
SELECT l.name AS language,
       f.name AS filter,
       f.description,
       f.filter_rule,
       lf.filter_value
FROM languages AS l
JOIN language_filters AS lf
    ON l.language_id = lf.language_id
JOIN filters AS f
    ON lf.filter_id = f.filter_id;

-- Index for searching by word meaning
CREATE INDEX
idx_words_meaning
ON words(meaning)

-- Create filter options
INSERT INTO filters (
    name,
    description,
    filter_rule
) VALUES (
    "require vowel",
    "only allow words with at least one vowel",
    "require_vowel"
);

INSERT INTO filters (
    name,
    description,
    filter_rule
) VALUES (
    "max vowel",
    "sets maximum vowels in a row",
    "max_vowel"
);

INSERT INTO filters (
    name,
    description,
    filter_rule
) VALUES (
    "max cluster",
    "sets maximum consonants in a row",
    "max_cluster"
);

INSERT INTO filters (
    name,
    description,
    filter_rule
) VALUES (
    "enforceZipf",
    "choose phonemes based on frequency. First phoneme is most common",
    "enforceZipf"
);