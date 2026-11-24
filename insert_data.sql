PRAGMA foreign_keys = ON;

-- fonts
INSERT INTO fonts (
    name,
    file_path
) values (
    "fontA",
    "/path/A"
);

INSERT INTO fonts (
    name,
    file_path
) values (
    "fontB",
    "/path/B"
);

INSERT INTO fonts (
    name,
    file_path
) values (
    "fontC",
    "/path/C"
);

INSERT INTO fonts (
    name,
    file_path
) values (
    "fontD",
    "/path/D"
);


-- languages

INSERT INTO languages (
    name,
    phonemes,
    vowels,
    clusters,
    font_id
) values (
    "langA",
    "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z",
    "A E I O U",
    "SH, CH, TH",
    1
);

INSERT INTO languages (
    name,
    phonemes,
    vowels,
    clusters,
    font_id
) values (
    "langB",
    "S E T V F U O A a N M",
    "E U O A",
    "ST FN SM",
    2
);

INSERT INTO languages (
    name,
    phonemes,
    vowels,
    clusters,
    font_id
) values (
    "langC",
    "K T G P R F D B Z S A I U E O N Y",
    "A I U E O",
    "",
    3
);

INSERT INTO languages (
    name,
    phonemes,
    vowels,
    clusters,
    font_id
) values (
    "langD",
    "ka ba ra ke be re ki bi ri",
    "",
    "kaka keke riri",
    4
);

INSERT INTO languages (
    name,
    phonemes,
    vowels,
    clusters,
    font_id
) values (
    "langE",
    "b d f g Z j n m a A e i o O U",
    "a A e i o O U",
    "dj ng",
    1
);

-- words

INSERT INTO words (
    word,
    meaning,
    pronunciation,
    language_id
) values (
    "dog",
    "dog",
    "",
    1
);

INSERT INTO words (
    word,
    meaning,
    pronunciation,
    language_id
) values (
    "SEaNUFN",
    "dog",
    "SEN-uh-fin",
    2
);

INSERT INTO words (
    word,
    meaning,
    pronunciation,
    language_id
) values (
    "inu",
    "dog",
    "EE-noo",
    3
);

INSERT INTO words (
    word,
    meaning,
    pronunciation,
    language_id
) values (
    "kakari",
    "cat",
    "ka-KA-ree",
    4
);

INSERT INTO words (
    word,
    meaning,
    pronunciation,
    language_id
) values (
    "rebiba",
    "horse",
    "rey-BEE-ba",
    4
);

-- names

INSERT INTO names (
    name,
    type,
    notes,
    language_id
) values (
    "Audrey",
    "given name",
    "hehe thats my name!",
    1
);

INSERT INTO names (
    name,
    type,
    notes,
    language_id
) values (
    "TEVFUA",
    "city",
    "coastal village",
    2
);

INSERT INTO names (
    name,
    type,
    notes,
    language_id
) values (
    "TOKIYO",
    "city",
    "capital of Japan",
    3
);

INSERT INTO names (
    name,
    type,
    notes,
    language_id
) values (
    "SAKURA",
    "given name",
    "means cherry flower",
    3
);

INSERT INTO names (
    name,
    type,
    notes,
    language_id
) values (
    "DOMITROVIC",
    "family name",
    "",
    1
);

-- filters
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
    "ends in o",
    "regex: only allow words ending in o",
    ".*o"
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
    "max vowel",
    "sets maximum vowels in a row",
    "max_vowel"
);

-- language filters
INSERT INTO language_filters (
    filter_id,
    language_id,
    filter_value,
    is_active
) VALUES (
    4,
    3,
    1,
    True
);

INSERT INTO language_filters (
    filter_id,
    language_id,
    filter_value,
    is_active
) VALUES (
    3,
    1,
    3,
    True
);

INSERT INTO language_filters (
    filter_id,
    language_id,
    filter_value,
    is_active
) VALUES (
    2,
    1,
    -1,
    False
);

INSERT INTO language_filters (
    filter_id,
    language_id,
    filter_value,
    is_active
) VALUES (
    4,
    1,
    -1,
    True
);