from flask import Flask, request, send_file
import sqlite3
import random
import os
from html import escape

# Required Application Functionality Locations:
#1. Search or Browse Data: Languages page (376), Names page (461)
#2. Display Related Data: Words page (328), MakeRandomWord (104)
#3. Add Data: names page (461), create words (961)
#4. Update or Delete Data: view language (552, 561)
#5. Summary or Report: count(*) in view language (602)
#6. Additional Meaningful Operation: these are scattered all over the place. View languages does some fun stuff with the filters

app = Flask(__name__)
# PORT = 3000
# DATABASE = 'data.db'
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 3000
DATABASE = os.path.join(APP_DIR, 'data.db')
SCHEMA = os.path.join(APP_DIR, 'createschema.sql')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return main_page()

@app.route('/name')
def name():
    return '<h1>Audrey Domitrovic</h1>'



#####################
# MAKE_RANDOM_WORD: #
#####################

# A function that generates a word with n phonemes following the given language's requirements
# used in create-words to make candidates
def makeRandomWord(language, n):
    import re

    conn = get_db_connection()

    language_row = conn.execute(
        'SELECT language_id, phonemes, vowels, clusters '
        'FROM languages WHERE name = ?',
        (language,)
    ).fetchone()

    if language_row is None:
        conn.close()
        raise ValueError('Language not found.')

    phonemes = (language_row['phonemes'] or '').split()
    vowels = (language_row['vowels'] or '').split()
    clusters = (language_row['clusters'] or '').split()

    filters = conn.execute(
        #2. Used internally for the algorithm
        'SELECT f.name, f.filter_rule, lf.filter_value '
        'FROM language_filters AS lf '
        'JOIN filters AS f ON f.filter_id = lf.filter_id '
        'WHERE lf.language_id = ? AND lf.is_active = 1',
        (language_row['language_id'],)
    ).fetchall()

    conn.close()

    if not phonemes:
        raise ValueError('The language has no phonemes.')

    filter_values = {}
    regex_filters = []

    for current_filter in filters:
        filter_name = current_filter['name']
        filter_value = current_filter['filter_value']
        filter_values[filter_name] = filter_value

        if filter_name not in {
            'enforceZipf',
            'require_vowel',
            'max_cluster',
            'common_cluster',
            'max_vowel'
        }:
            try:
                regex_filters.append(
                    re.compile(current_filter['filter_rule'])
                )
            except (re.error, TypeError):
                # Ignore malformed or missing regular expressions.
                pass

    def choose_phoneme():
        if 'enforceZipf' not in filter_values:
            return random.choice(phonemes)

        # Higher probability for earlier phonemes
        total = len(phonemes) * (len(phonemes) + 1) / 2
        random_value = random.random() * total
        running_total = 0

        for index, phoneme in enumerate(phonemes):
            running_total += len(phonemes) - index
            if random_value < running_total:
                return phoneme

        return phonemes[-1]

    max_attempts = 10000

    for _ in range(max_attempts):
        # this is the issue: it isn't checking phonemes until after the word is fully generated. 
        # Rule out bad phonemes/clusters as you make the word instead to get rid of them quicker
        # for another day. Otherwise, langB, D, and E will generate words currently

        candidate_phonemes = [
            choose_phoneme()
            for _ in range(n)
        ]
        word = ''.join(candidate_phonemes)

        if 'require_vowel' in filter_values and vowels:
            if not any(
                phoneme in vowels
                for phoneme in candidate_phonemes
            ):
                continue

        consonant_runs = []
        vowel_runs = []

        current_consonant_run = []
        current_vowel_run = []

        for phoneme in candidate_phonemes:
            if vowels and phoneme in vowels:
                if current_consonant_run:
                    consonant_runs.append(current_consonant_run)
                    current_consonant_run = []
                current_vowel_run.append(phoneme)
            else:
                if current_vowel_run:
                    vowel_runs.append(current_vowel_run)
                    current_vowel_run = []
                current_consonant_run.append(phoneme)

        if current_consonant_run:
            consonant_runs.append(current_consonant_run)
        if current_vowel_run:
            vowel_runs.append(current_vowel_run)

        if 'max_cluster' in filter_values and consonant_runs:
            try:
                maximum_cluster = int(filter_values['max_cluster'])
                if any(
                    len(cluster) > maximum_cluster
                    for cluster in consonant_runs
                ):
                    continue
            except (TypeError, ValueError):
                pass

        if 'common_cluster' in filter_values and clusters:
            uncommon_cluster = any(
                len(cluster) > 1 and ' '.join(cluster) not in clusters
                for cluster in consonant_runs
            )

            if uncommon_cluster:
                try:
                    denial_percentage = float(
                        filter_values['common_cluster']
                    )
                    if random.random() < denial_percentage / 100:
                        continue
                except (TypeError, ValueError):
                    pass

        if 'max_vowel' in filter_values and vowel_runs:
            try:
                maximum_vowels = int(filter_values['max_vowel'])
                if any(
                    len(vowel_run) > maximum_vowels
                    for vowel_run in vowel_runs
                ):
                    continue
            except (TypeError, ValueError):
                pass

        if any(
            regex.fullmatch(word) is None
            for regex in regex_filters
        ):
            continue

        return word

    raise ValueError(
        'Could not generate a word after many attempts. '
        'The language filters may be impossible to satisfy.'
    )

# TODO: edit word generation logic to actually be fast
# TODO: see if you can add font logic so that a language's font image appears on the summary page

####################
# HELPER FUNCTIONS #
####################

# Adds the same menu to the top of each page and returns HTML with the incoming body
def page(title, body):
    return f"""
    <!doctype html>
    <html>
    <head><title>{escape(title)}</title></head>
    <body>
    <h1>{escape(title)}</h1>
    <p>
      <a href="/">Home</a> |
      <a href="/words">Words</a> |
      <a href="/languages">Languages</a> |
      <a href="/filters">Filters</a> |
      <a href="/names">Names</a> |
      <a href="/view-language">Language Summary</a> |
      <a href="/edit-language">Edit Language</a> |
      <a href="/create-words">Generate Words</a> |
      <a href="/upload-font">Upload Font</a>
    </p>
    {body}
    </body>
    </html>
    """

def field(value):
    return escape('' if value is None else str(value))

# reusable HTML for choosing a language
def language_options(languages, selected=None):
    result = '<option value="">-- select language --</option>'
    for language in languages:
        chosen = ' selected' if str(language['language_id']) == str(selected) else ''
        result += (
            f'<option value="{language["language_id"]}"{chosen}>'
            f'{field(language["name"])}</option>'
        )
    return result

# reusable SQL for getting all languages
def all_languages():
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT language_id, name FROM languages ORDER BY name'
    ).fetchall()
    conn.close()
    return rows

# loading function for ensuring that the database exists else running createschema.sql to create it
def startupDatabase():
    if os.path.exists(DATABASE):
        return

    if not os.path.isfile(SCHEMA):
        raise FileNotFoundError(f'Schema file not found: {SCHEMA}')

    conn = sqlite3.connect(DATABASE)
    try:
        with open(SCHEMA, 'r', encoding='utf-8') as schema_file:
            conn.executescript(schema_file.read())
    finally:
        conn.close()

startupDatabase()

########
# HOME #
########

# the landing page. Update the body to remove the secondary menu if time permits
@app.route('/')
def main_page():
    return page('Conlang Application', """
    <p>Use this application to create words and names for all your conlang needs. This application supports multiple languages using alphabets or syllabaries.
    </p>
    <ul>
      <li><a href="/words">Search Words</a></li>
      <li><a href="/languages">View Languages</a></li>
      <li><a href="/filters">View Filters</a></li>
      <li><a href="/names">Search Names</a></li>
      <li><a href="/view-language">Language Summary</a></li>
      <li><a href="/edit-language">Create/Update Language</a></li>
      <li><a href="/create-words">Generate Words</a></li>
      <li><a href="/upload-font">Upload Font</a></li>
    </ul>
    """)



#########
# WORDS #
#########

# Words page, which allows searching of the words table by language or meaning
@app.route('/words', methods=['GET', 'POST'])
def search_words():
    language = request.form.get('language', '') if request.method == 'POST' else request.args.get('language', '')
    meaning = request.form.get('meaning', '') if request.method == 'POST' else request.args.get('meaning', '')

    #2. The searching mechanism to lookup words by meaning or language
    sql = (
        'SELECT w.word, w.meaning, w.pronunciation '
        'FROM words AS w JOIN languages AS l ON w.language_id = l.language_id'
    )
    conditions = []
    values = []

    if language:
        conditions.append('l.name = ?')
        values.append(language)
    if meaning:
        conditions.append('w.meaning = ?')
        values.append(meaning)

    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)
    sql += ' ORDER BY w.word'

    conn = get_db_connection()
    rows = conn.execute(sql, values).fetchall()
    conn.close()

    body = f"""
    <form method="post">
      Language: <input name="language" value="{field(language)}">
      Meaning: <input name="meaning" value="{field(meaning)}">
      <button type="submit">Search</button>
    </form>
    <table border="1">
      <tr><th>Word</th><th>Meaning</th><th>Pronunciation</th></tr>
    """
    for row in rows:
        body += (
            f'<tr><td>{field(row["word"])}</td>'
            f'<td>{field(row["meaning"])}</td>'
            f'<td>{field(row["pronunciation"])}</td></tr>'
        )
    body += '</table>'
    return page('Search Words', body)



#############
# LANGUAGES #
#############

# languages page: displays all languages currently in the database
@app.route('/languages')
def view_languages():
    conn = get_db_connection()

    #1. View language names
    rows = conn.execute('SELECT name FROM languages ORDER BY name').fetchall()
    conn.close()

    body = '<table border="1"><tr><th>Name</th></tr>'
    for row in rows:
        body += f'<tr><td>{field(row["name"])}</td></tr>'
    body += '</table>'
    return page('Languages', body)



###########
# FILTERS #
###########

# shows all filters currently available, and allows the addition of new ones
@app.route('/filters', methods=['GET', 'POST'])
def view_filters():
    message = ''
    if request.method == 'POST':
        name = request.form.get('name', '')
        description = request.form.get('description', '')
        rule = request.form.get('filter_rule', '')

        if not name or not rule:
            message = '<p>Filter name and rule are required.</p>'
        else:
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO filters (name, description, filter_rule) VALUES (?, ?, ?)',
                    (name, description, rule)
                )
                conn.commit()
                message = '<p>Filter created.</p>'
            except sqlite3.IntegrityError:
                message = '<p>Could not create filter. Check the values.</p>'
            finally:
                conn.close()

    conn = get_db_connection()
    rows = conn.execute(
        'SELECT name, description, filter_rule FROM filters ORDER BY name'
    ).fetchall()
    conn.close()

    body = message + """
    <form method="post">
      Name: <input name="name" required><br>
      Description: <input name="description"><br>
      Filter rule: <input name="filter_rule" required><br>
      <button type="submit">Create Filter</button>
    </form>
    <table border="1">
      <tr><th>Name</th><th>Description</th><th>Rule</th></tr>
    """
    for row in rows:
        body += (
            f'<tr><td>{field(row["name"])}</td>'
            f'<td>{field(row["description"])}</td>'
            f'<td>{field(row["filter_rule"])}</td></tr>'
        )
    body += '</table>'
    return page('Filters', body)



#########
# NAMES #
#########

# View names (proper nouns) by language, or insert a new name in a given language
@app.route('/names', methods=['GET', 'POST'])
def search_names():
    language = request.form.get('language', '') if request.method == 'POST' else request.args.get('language', '')
    message = ''

    conn = get_db_connection()
    languages = conn.execute(
        # 1
        'SELECT language_id, name FROM languages ORDER BY name'
    ).fetchall()

    if request.method == 'POST' and request.form.get('add_name') == '1':
        name = request.form.get('name', '')
        name_type = request.form.get('type', '')
        notes = request.form.get('notes', '')
        language_id = request.form.get('language_id', '')

        if not name or not name_type or not language_id:
            message = '<p>Name, type, and language are required.</p>'
        else:
            try:
                conn.execute(
                    # 3
                    'INSERT INTO names (name, type, notes, language_id) VALUES (?, ?, ?, ?)',
                    (name, name_type, notes, language_id)
                )
                conn.commit()
                message = '<p>Name added.</p>'
            except sqlite3.IntegrityError:
                message = '<p>Could not add name.</p>'

    sql = (
        'SELECT n.name, n.type, n.notes '
        'FROM names AS n JOIN languages AS l ON n.language_id = l.language_id'
    )
    values = []
    if language:
        sql += ' WHERE l.name = ?'
        values.append(language)
    sql += ' ORDER BY n.name'
    rows = conn.execute(sql, values).fetchall()
    conn.close()

    body = f"""
    {message}
    <form method="post">
      <input type="hidden" name="add_name" value="0">
      Language name: <input name="language" value="{field(language)}">
      <button type="submit">Search</button>
    </form>
    <h2>Add Name</h2>
    <form method="post">
      <input type="hidden" name="add_name" value="1">
      Name: <input name="name" required><br>
      Type: <input name="type" required><br>
      Notes: <input name="notes"><br>
      Language: <select name="language_id" required>
        {language_options(languages)}
      </select><br>
      <button type="submit">Add Name</button>
    </form>
    <table border="1">
      <tr><th>Name</th><th>Type</th><th>Notes</th></tr>
    """
    for row in rows:
        body += (
            f'<tr><td>{field(row["name"])}</td>'
            f'<td>{field(row["type"])}</td>'
            f'<td>{field(row["notes"])}</td></tr>'
        )
    body += '</table>'
    return page('Search Names', body)



####################
# LANGUAGE SUMMARY #
####################

# View information about a language, and update its filter list
@app.route('/view-language', methods=['GET', 'POST'])
def view_language():
    language = request.form.get('language', '') or request.args.get('language', '')
    message = ''

    conn = get_db_connection()

    # Handle adding, updating, or deleting a language-specific filter.
    if request.method == 'POST' and request.form.get('filter_action'):
        action = request.form.get('filter_action')
        filter_id = request.form.get('filter_id', '')
        filter_value = request.form.get('filter_value', '0')
        is_active = request.form.get('is_active', '1')

        language_row = conn.execute(
            'SELECT language_id FROM languages WHERE name = ?',
            (language,)
        ).fetchone()

        if language_row is None:
            conn.close()
            return '<h1>Language not found</h1>', 404

        language_id = language_row['language_id']

        try:
            if action == 'add':
                conn.execute(
                    #4.
                    'INSERT INTO language_filters '
                    '(language_id, filter_id, filter_value, is_active) '
                    'VALUES (?, ?, ?, ?)',
                    (language_id, filter_id, filter_value, is_active)
                )
                message = '<p>Filter added.</p>'

            elif action == 'update':
                conn.execute(
                    # 4.
                    'UPDATE language_filters '
                    'SET filter_value = ?, is_active = ? '
                    'WHERE language_id = ? AND filter_id = ?',
                    (filter_value, is_active, language_id, filter_id)
                )
                message = '<p>Filter updated.</p>'

            elif action == 'delete':
                conn.execute(
                    #4.
                    'DELETE FROM language_filters '
                    'WHERE language_id = ? AND filter_id = ?',
                    (language_id, filter_id)
                )
                message = '<p>Filter deleted.</p>'

            conn.commit()

        except sqlite3.IntegrityError:
            message = '<p>That filter is already assigned, or the filter does not exist.</p>'

    body = f"""
    {message}
    <form method="post">
      Language:
      <input name="language" value="{field(language)}" required>
      <button type="submit">View</button>
    </form>
    """

    if not language:
        conn.close()
        return page('Language Summary', body)

    language_row = conn.execute(
        'SELECT language_id, name, phonemes, vowels, clusters '
        'FROM languages WHERE name = ?',
        (language,)
    ).fetchone()

    if language_row is None:
        conn.close()
        return page(
            'Language Summary',
            body + '<p>Language not found.</p>'
        ), 404

    #5.
    count = conn.execute(
        'SELECT count(*) AS total FROM words '
        'WHERE language_id = ?',
        (language_row['language_id'],)
    ).fetchone()['total']

    filters = conn.execute(
        'SELECT lf.filter_id, f.name, f.description, f.filter_rule, '
        'lf.filter_value, lf.is_active '
        'FROM language_filters AS lf '
        'JOIN filters AS f ON f.filter_id = lf.filter_id '
        'WHERE lf.language_id = ?',
        (language_row['language_id'],)
    ).fetchall()

    available_filters = conn.execute(
        'SELECT filter_id, name FROM filters ORDER BY name'
    ).fetchall()

    conn.close()

    body += f"""
    <h2>{field(language_row["name"])}</h2>
    <p>Phonemes: {field(language_row["phonemes"])}</p>
    <p>Vowels: {field(language_row["vowels"])}</p>
    <p>Clusters: {field(language_row["clusters"])}</p>
    <p>Word count: {count}</p>

    <p>
      <a href="/edit-language?language_id={language_row["language_id"]}">
        Edit language
      </a>
      |
      <a href="/words?language={field(language)}">
        View words
      </a>
    </p>

    <h3>Filters for this language</h3>
    """

    if filters:
        body += """
        <table border="1">
          <tr>
            <th>Filter</th>
            <th>Description</th>
            <th>Rule</th>
            <th>Value</th>
            <th>Active</th>
            <th>Actions</th>
          </tr>
        """

        for item in filters:
            body += f"""
            <tr>
              <td>{field(item["name"])}</td>
              <td>{field(item["description"])}</td>
              <td>{field(item["filter_rule"])}</td>
              <td>
                <form method="post">
                  <input type="hidden" name="language"
                         value="{field(language)}">
                  <input type="hidden" name="filter_id"
                         value="{item["filter_id"]}">
                  <input name="filter_value"
                         value="{field(item["filter_value"])}">
              </td>
              <td>
                  <select name="is_active">
                    <option value="1"
                      {"selected" if item["is_active"] else ""}>
                      Yes
                    </option>
                    <option value="0"
                      {"selected" if not item["is_active"] else ""}>
                      No
                    </option>
                  </select>
              </td>
              <td>
                  <button name="filter_action" value="update">
                    Update
                  </button>
                </form>

                <form method="post">
                  <input type="hidden" name="language"
                         value="{field(language)}">
                  <input type="hidden" name="filter_id"
                         value="{item["filter_id"]}">
                  <button name="filter_action" value="delete">
                    Delete
                  </button>
                </form>
              </td>
            </tr>
            """

        body += '</table>'
    else:
        body += '<p>No filters assigned to this language.</p>'

    body += f"""
    <h3>Add Existing Filter</h3>
    <form method="post">
      <input type="hidden" name="language" value="{field(language)}">

      <select name="filter_id" required>
    """

    for item in available_filters:
        body += (
            f'<option value="{item["filter_id"]}">'
            f'{field(item["name"])}</option>'
        )

    body += """
      </select>

      Value:
      <input name="filter_value" value="0">

      Active:
      <select name="is_active">
        <option value="1">Yes</option>
        <option value="0">No</option>
      </select>

      <button name="filter_action" value="add">
        Add Filter
      </button>
    </form>
    """

    return page('Language Summary', body)



#################
# EDIT LANGUAGE #
#################

# Edit the values of a language, or add a new one
@app.route('/edit-language', methods=['GET', 'POST'])
def edit_language():
    message = ''
    selected = request.form.get('language_id') or request.args.get('language_id', '')

    conn = get_db_connection()

    if request.method == 'POST':
        action = request.form.get('action')
        selected = request.form.get('language_id', '')
        name = request.form.get('name', '')
        phonemes = request.form.get('phonemes', '')
        vowels = request.form.get('vowels', '')
        clusters = request.form.get('clusters', '')
        font_id = request.form.get('font_id') or None

        if not name or not phonemes:
            message = '<p>Name and phonemes are required.</p>'
        else:
            try:
                if action == 'update' and selected:
                    conn.execute(
                        'UPDATE languages SET name = ?, phonemes = ?, vowels = ?, clusters = ?, font_id = ? '
                        'WHERE language_id = ?',
                        (name, phonemes, vowels, clusters, font_id, selected)
                    )
                    message = '<p>Language updated.</p>'
                else:
                    cursor = conn.execute(
                        'INSERT INTO languages (name, phonemes, vowels, clusters, font_id) '
                        'VALUES (?, ?, ?, ?, ?)',
                        (name, phonemes, vowels, clusters, font_id)
                    )
                    selected = cursor.lastrowid
                    message = '<p>Language created.</p>'
                conn.commit()
            except sqlite3.IntegrityError:
                message = '<p>Could not save language.</p>'

    languages = conn.execute(
        'SELECT language_id, name, phonemes, vowels, clusters, font_id '
        'FROM languages ORDER BY name'
    ).fetchall()
    fonts = conn.execute(
        'SELECT font_id, name FROM fonts ORDER BY name'
    ).fetchall()

    current = None
    if selected:
        current = conn.execute(
            'SELECT language_id, name, phonemes, vowels, clusters, font_id '
            'FROM languages WHERE language_id = ?',
            (selected,)
        ).fetchone()

    filters = conn.execute(
        'SELECT filter_id, name, description, filter_rule FROM filters ORDER BY name'
    ).fetchall()

    if current:
        language_filters = conn.execute(
            'SELECT f.name, f.description, lf.filter_value, lf.is_active '
            'FROM language_filters AS lf JOIN filters AS f ON f.filter_id = lf.filter_id '
            'WHERE lf.language_id = ?',
            (selected,)
        ).fetchall()
    else:
        language_filters = []

    conn.close()

    current = current or {
        'name': '', 'phonemes': '', 'vowels': '', 'clusters': '', 'font_id': ''
    }

    font_options = '<option value="">-- no font --</option>'
    for font in fonts:
        chosen = ' selected' if str(font['font_id']) == str(current['font_id']) else ''
        font_options += f'<option value="{font["font_id"]}"{chosen}>{field(font["name"])}</option>'

    filter_options = ''
    for item in filters:
        filter_options += f'<option value="{item["filter_id"]}">{field(item["name"])}</option>'

    body = f"""
    {message}
    <form method="get">
      <select name="language_id">
        {language_options(languages, selected)}
      </select>
      <button type="submit">Load</button>
    </form>
    <form method="post">
      <input type="hidden" name="language_id" value="{field(selected)}">
      Name: <input name="name" value="{field(current["name"])}" required><br>
      Phonemes: <input name="phonemes" value="{field(current["phonemes"])}" required><br>
      Vowels: <input name="vowels" value="{field(current["vowels"])}"><br>
      Clusters: <input name="clusters" value="{field(current["clusters"])}"><br>
      Font: <select name="font_id">{font_options}</select><br>
      <button name="action" value="create">Create</button>
      <button name="action" value="update">Update</button>
    </form>
    """

    if selected:
        body += f"""
        <h2>Language Filters</h2>
        <form method="post">
          <input type="hidden" name="language_id" value="{field(selected)}">
          <select name="filter_id">{filter_options}</select>
          Value: <input name="filter_value" value="0">
          <button name="filter_action" value="add">Add Filter</button>
        </form>
        <form method="post">
          <input type="hidden" name="language_id" value="{field(selected)}">
          Filter ID: <input name="filter_id" required>
          <button name="filter_action" value="delete">Delete Filter</button>
        </form>
        <table border="1">
          <tr><th>Filter</th><th>Description</th><th>Value</th><th>Active</th></tr>
        """
        for item in language_filters:
            body += (
                f'<tr><td>{field(item["name"])}</td>'
                f'<td>{field(item["description"])}</td>'
                f'<td>{field(item["filter_value"])}</td>'
                f'<td>{field(item["is_active"])}</td></tr>'
            )
        body += '</table>'

    return page('Create/Update Language', body)



################
# CREATE WORDS #
################

# Add words to a language, plus generate new candidate words that fit the language
@app.route('/create-words', methods=['GET', 'POST'])
def create_words():
    languages = all_languages()
    selected = request.form.get('language_id', '')
    generated = []
    message = ''

    if request.method == 'POST' and request.form.get('action') == 'generate':
        try:
            length = int(request.form.get('length', '3'))
        except ValueError:
            return page('Generate Words', '<p>Length must be a number.</p>'), 400

        if length < 1:
            return page('Generate Words', '<p>Length must be positive.</p>'), 400

        conn = get_db_connection()
        language_row = conn.execute(
            'SELECT name FROM languages WHERE language_id = ?',
            (selected,)
        ).fetchone()
        conn.close()

        if language_row is None:
            return page('Generate Words', '<p>Language not found.</p>'), 404

        language = language_row['name']

        try:
            attempts = 0
            max_attempts = 1000

            while len(generated) < 10 and attempts < max_attempts:
                attempts += 1
                word = makeRandomWord(language, length)

                if word not in generated:
                    generated.append(word)

            if len(generated) < 10:
                message = (
                    '<p>Could not generate 10 unique words. '
                    'The word length or filters may allow too few possibilities.</p>'
                )

        except ValueError as error:
            message = f'<p>{field(error)}</p>'

    body = f"""
    {message}
    <form method="post">
      <select name="language_id" required>
        {language_options(languages, selected)}
      </select>
      Length:
      <input type="number" name="length" value="3" min="1" required>
      <button name="action" value="generate">Generate</button>
    </form>
    """

    if generated:
        body += '<table border="1"><tr><th>Generated Word</th></tr>'
        for word in generated:
            body += f'<tr><td>{field(word)}</td></tr>'
        body += '</table>'

    body += """
    <h2>Add Word</h2>
    <form method="post">
      Word: <input name="word" required><br>
      Meaning: <input name="meaning" required><br>
      Pronunciation: <input name="pronunciation"><br>
      Language: <select name="language_id" required>
    """
    body += language_options(languages, selected)
    body += """
      </select><br>
      <button name="action" value="add">Add Word</button>
    </form>
    """

    if request.method == 'POST' and request.form.get('action') == 'add':
        conn = get_db_connection()
        conn.execute(
            #3.
            'INSERT INTO words '
            '(word, meaning, pronunciation, language_id) '
            'VALUES (?, ?, ?, ?)',
            (
                request.form.get('word', ''),
                request.form.get('meaning', ''),
                request.form.get('pronunciation', ''),
                request.form.get('language_id')
            )
        )
        conn.commit()
        conn.close()
        body += '<p>Word added.</p>'

    return page('Generate Words', body)



###############
# UPLOAD FONT #
###############

# allows uploading of font files that display the script for a language
@app.route('/upload-font', methods=['GET', 'POST'])
def upload_font():
    message = ''
    if request.method == 'POST':
        font_name = request.form.get('name', '')
        uploaded = request.files.get('font')

        if not font_name or uploaded is None or not uploaded.filename:
            message = '<p>Font name and file are required.</p>'
        else:
            os.makedirs('./fonts', exist_ok=True)
            filename = os.path.basename(uploaded.filename)
            path = os.path.join('./fonts', filename)
            uploaded.save(path)

            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO fonts (name, file_path) VALUES (?, ?)',
                    (font_name, path)
                )
                conn.commit()
                message = '<p>Font uploaded.</p>'
            except sqlite3.IntegrityError:
                message = '<p>Could not add font. The name may already exist.</p>'
            finally:
                conn.close()

    return page('Upload Font', f"""
    {message}
    <form method="post" enctype="multipart/form-data">
      Font name: <input name="name" required><br>
      File: <input type="file" name="font" required><br>
      <button type="submit">Upload</button>
    </form>
    """)

# helper for finding a font file
@app.route('/font-file')
def font_file():
    path = request.args.get('path', '')
    if not path or not os.path.isfile(path):
        return '<h1>Font file not found</h1>', 404
    return send_file(path)

# run this thing
app.run(port=3000)

