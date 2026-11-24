# Audrey's Conlang Dictionary
Audrey's Conlang Dictionary is a browser-based tool that helps you generate, define, and keep track of words in made up languages (known as 'constructed languages' or 'conlangs'). This application is intended for worldbuilders, linguists, and anyone else who wants to make their own Klingon, Elvish, or Esperanto. 

It is made as a class project. While it is sufficient for this class, it is not intended as a final product, and likely won't be updated. Regardless, you are welcome to use or remix it if you find it helpful. 

### Setup instructions:
1. Programming language: Python3 with flask. 
    Uses inline HTML and SQLite3
2. Versions: Python3, sqlite3
3. Required packages: flask, sqlite3
4. Installation commands: installation matches our in class lectures about flask
5. (OPTIONAL) The application will automatically read createschema.sql to create the database. This will result in an empty database you can add data to yourself. 
    To instead initialize with example data, manually run the following before starting the application:
    > sqlite3 data.db
    
    > .read createschema.sql
    
    > .read insert_data.sql
6. Start the application: 
    > python3 app.py
    
    > visit http://localhost:3000 in your browser

### Required Application Functionality Locations:
1. Search or Browse Data: Languages page (376), Names page (461)
2. Display Related Data: Words page (328), MakeRandomWord (104)
3. Add Data: names page (461), create words (961)
4. Update or Delete Data: view language (552, 561)
5. Summary or Report: count(*) in view language (602)
6. Additional Meaningful Operation: these are scattered all over the place. Language Summary (496) does some fun stuff with the filter interface. 

### Major Application Functionality:
1. Make or update new languages 
2. Generate candidate words in a language
3. Add words or names to a language and define them
4. Store and search existing words and names

### Notes: 
This got long due to all the html and sql, so I have added the line numbers for some examples. There are other examples throughout to create the entire application. 

It is not necessary to run queries.sql in order to achieve full functionality of the final program, but it is included as a deliverable regardless and demonstrates some of the queries that the application handles. It can be run manually using sqlite3's .read function (seen in step 5). 

Likewise, transaction.sql (which will fully delete the language with id 1) is not necessary for the final program's functionality. It can also be run manually using sqlite3's .read function. 

### Known Limitations:

There is one issue where the generate words function times out in some languages. It will display an error about this. This is related to the makeRandomWords implementation, but does not affect any of the database functionality. To reliably generate words, use langB, langD, or langE in the example data. 
If using your own data, avoid activating the max vowel or max cluster filters.  

The font uploading functionality is a stub. You can upload a file and link it to a language, but the image will never be displayed. 
