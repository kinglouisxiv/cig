# cig.py

 Comic Indexer Generator

gci.py is a python script which reads a text file of "Key: value" pairs (index file), and a file of "tag \t definition" pairs (tags file), outputs html parts for an index page.

The html output is intended to work with handler.js from [snipergirl/gunnerkrigg](https://github.com/snipergirl/gunnerkrigg) for select/show/hide of commonly tagged items -- flat file, no database.


```
usage: gci.py [-h] [-i INPATH] [-o OUTPATH] [-x NDEX] [-t TAGS] [-u UPDATE]
              [-l LIST] [-b BOOK] [-p PAGES]

Convert index & tags to html part files out

optional arguments:
  -h, --help            show this help message and exit
  -i INPATH, --inpath INPATH
                        input path (default: )
  -o OUTPATH, --outpath OUTPATH
                        output path (default: )
  -x NDEX, --ndex NDEX  index file (default: index.txt)
  -t TAGS, --tags TAGS  tags file (default: tags.txt)
  -u UPDATE, --update UPDATE
                        update part filename (default: updated.html)
  -l LIST, --list LIST  list of tags filename (default: tags.html)
  -b BOOK, --book BOOK  chapter/book list filename (default: chapter.html)
  -p PAGES, --pages PAGES
                        pages list filename (default: pages.html)
```

## The Index file

Key	| Use
-----	|----
page:	| comic page ID and link: heads a comic page entry. 
url:	| the actual comic page url (no url, no link)
tag:	| a tag for the page's story: character, item, location, etc.
desc:	| a description of the page's story
note:	| other non-story text (_not yet implemented_)
;	| comment line: internal, not for processing,

**Suggestion**: page: should be left-aligned, other keys should have leading whitespace to clearly show their subordinate relationship to the preceding page:.


The Tag File
---------------

The tags definition file is: 

- comments, marked by leading semicolon ";"
- tag & definition pairs, tab separated

**tag** as above: a tag should be valid as an html class. Last definition wins

**Processing**: definition text is processed for simple Markdown formatting & links, and html passthrough.

----

Example input files at 





