.mode box
PRAGMA foreign_keys = ON;

--1 Filtering and sorting
-- used to get alphabet data for generating words
SELECT phonemes, 
       vowels, 
       clusters 
FROM languages 
WHERE name = 'langA';

-- 2 Inner join
-- get all words from a language, used for words display
SELECT w.word,
       w.meaning,
       w.pronunciation
FROM words AS w
INNER JOIN languages AS l
    ON w.language_id = l.language_id
WHERE l.name = 'langA'
ORDER BY w.meaning;

-- 3 Left Join
-- Displays names with their languages
SELECT l.name,
       n.name
FROM languages AS l
LEFT JOIN names AS n
    ON l.language_id = n.language_id
ORDER BY l.name;

-- 4: three table join
-- finds filters active for a given language
SELECT f.name
FROM languages AS l
JOIN language_filters AS lf
    ON l.language_id = lf.language_id
JOIN filters AS f
    ON lf.filter_id = f.filter_id
WHERE l.name = 'langA';

-- 5. Aggregate Query
-- Counts words in each language
SELECT l.name,
       COUNT(w.word) AS word_count
FROM languages AS l
JOIN words AS w
    ON l.language_id = w.language_id
GROUP BY l.name;

-- 6. Group By and Having
-- count names in languages and only display languages with at least 1 name
SELECT l.name,
       COUNT(n.name) AS name_count
FROM languages AS l
JOIN names AS n
    ON l.language_id = n.language_id
GROUP BY l.name
HAVING COUNT(n.name) > 0
ORDER BY COUNT(n.name) DESC;

-- 7. Subquery
-- finds words which share a meaning across languages
SELECT word
FROM words
WHERE meaning IN (
    SELECT meaning
    FROM words
    GROUP BY meaning
    HAVING COUNT(*) > 1
);

-- 8. Set Operation
-- return every language-word or language-name pair to see all items created so far
-- could be used as another view
SELECT language_id, 
       word AS item
FROM words
UNION 
SELECT language_id,
       name AS item
FROM names;

-- 9. View operation
-- look how short and sweet that is! no weird joins when I want to check something by language name
SELECT * 
FROM filters_by_lang 
WHERE name = 'langA'

