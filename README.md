# gci.py

Generalised Comic Indexer

gci.py builds formatted files listing comic pages with descriptions and tags for common elements into html parts for inclusion in a web page.

* Generalised -- which it isn't yet -- refers to the intention to make it handle different comic urls specified in the data files rather than hard coding into comic-specific versions of the script.

* Comic -- this is aimed at indexing page to page details of web comics, but the mechanism is pretty general and could be used for other tagged lists.

* Indexer -- ah, well, um, actually _someone_ has to do the actual indexing, this script just makes it prettier and more useful.

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

## Input files

### Index

The index file is a list of pages, with tab separated associated tags and comments and optional tag definitions. (Tab definitions can also be supplied in a separate file)

```
pageid <tab> tag <tab> ... <tab> tagN <tab>#text
@ <tab> tag1 <tab> text
; in-file comment - discarded in processing
```

lines starting:

**;**

- in line comments, discarded in processing

**@**

- in line tag definition -- deprecated: use a tags file

_url:_

- _**not yet implemented**, sets the url for subsequent pageids. Allows index file to be self-contained, and allows switching between, for instance, main and branch comics._

Line format otherwise:

**pageid** 

- usually the unique portion of the page's url: often a page number, or date, or title. Treated as a string.

**tag**

- there can be any number of tags (0--NN)
- tags must be unique when made lower case, and 
- must be valid as css class names (for the selection mechanism)
- tags starting "ch-" are also treated as chapter/book identifiers

**#**

- Start of text description or comment, which is processed for Markdown formatting.
- feature: there must not be tab characters after the #

### Tags

The tags file contains the tag definitions. A tag does not have to be defined to be used.

```
tag1 <tab> definition
; in line comment - discarded in processing
```

lines starting:

**;**

- in line comments, discarded in processing

Line format otherwise:

**tag**

- tags must be unique when made lower case, and 
- must be valid as css class names (for the selection mechanism)

**definition**

- text description or comment, which is processed for Markdown formatting









