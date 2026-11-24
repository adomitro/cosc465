-- transaction to remove all traces of a language

BEGIN;

-- remove all filters matching a language
DELETE FROM language_filters
WHERE language_id = 1;
-- remove all names matching a language
DELETE FROM names
WHERE language_id = 1;
-- remove all words matching a language
DELETE FROM words
WHERE language_id = 1;
-- delete the language itself
DELETE FROM languages
WHERE language_id = 1;

COMMIT;