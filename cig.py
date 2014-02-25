#! python
# -*- coding: utf-8 -*-

# version date 2014-02-23

import string
import collections
import codecs
import markdown
import argparse
import cgi

parser = argparse.ArgumentParser(
    description="Convert index & tags to html part files out",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-i", "--inpath",  help="input path", default="")
parser.add_argument("-o", "--outpath", help="output path", default="")
parser.add_argument("-x", "--ndex",    help="index file", default="index.txt")
parser.add_argument("-t", "--tags",    help="tags file", default="tags.txt")
parser.add_argument("-u", "--update",  help="update part filename", default="updated.html")
parser.add_argument("-l", "--list",    help="list of tags filename", default="tags.html")
parser.add_argument("-b", "--book",    help="chapter/book list filename", default="chapter.html")
parser.add_argument("-p", "--pages",   help="pages list filename", default="pages.html")
args = parser.parse_args()

if args.inpath > "":
    indexfile   = args.inpath + "/" + args.ndex # TODO: use os.path here?
    tagsfile    = args.inpath + "/" + args.tags
else:
    indexfile   = args.ndex
    tagsfile    = args.tags
if args.outpath > "":
    updatefile  = args.outpath + "/" + args.update
    listtagfile = args.outpath + "/" + args.list
    bookfile    = args.outpath + "/" + args.book
    pagesfile   = args.outpath + "/" + args.pages
else:
    updatefile  = args.update
    listtagfile = args.list
    bookfile    = args.book
    pagesfile   = args.pages
# #debug
# print "indexfile:   " + indexfile
# print "tagsfile:    " + tagsfile
# print "updatefile:  " + updatefile
# print "listtagfile: " + listtagfile
# print "bookfile:    " + bookfile
# print "pagesfile:   " + pagesfile
#
# junk = raw_input("type return: ")

tagdict = {}	# tags : definitions
# pagelist = []	# list of page lines
tagcount = collections.Counter()


def main():
    tags = 0
    pages = 0

    tags = TagsIn(tags)
    tags, pages = IndexIn(tags, pages)
    DateCountsOut(tags, pages)
    TagsOut()


def TagsIn(definedtags):
    ''' Read a pure tag source file, count tags, fill dictionary.

    file format:
        tag \t definition
    NB tag must be a valid html class, and unique

    Using Codecs now because of Markdown requirements later
    '''
    f = codecs.open(tagsfile, mode='r', encoding="utf-8")
    for line in f:
        stripline = line.strip()
        if stripline[0:1] == ';':                       # it's a comment
            print stripline
        else:
            field = stripline.split("\t")
            tagdict[field[0].strip()] = field[1].strip()
            definedtags += 1
    f.close()
    return definedtags

def IndexIn(definedtags, totalpages):
    ''' Read the page data, separate elements (tags, pages) into dicts and lists, print & discard comments
        Using Codecs now because of Markdown requirements later
    '''
    pageID = ""
    f = codecs.open(indexfile, mode='r', encoding="utf-8")
    for line in f:
        stripline = line.strip()     #remove leading, trailing whitespace
        if stripline[0:1] == ';':   # this is a comment
            print stripline
        elif stripline[0:5].lower() == "page:":
            # do new page stuff
            totalpages += 1
            if pageID > "":                         # there is a previous page, so output it
                PageOut (pageID, pageDesc, pageNote, pageTags, pageURL)
            else:                                   # this is the first page:
                f = codecs.open(pagesfile, mode='w', encoding="utf-8")  # clear the output ready to append
                f.close()
            pageID = stripline[5:]
            pageDesc = ""
            pageNote = ""
            pageTags = []
            pageURL = ""
        elif stripline[0:4].lower() == "url:":
            if pageID > "":
                # add a check for duplicate URLs
                pageURL = cgi.escape(stripline[4:].strip())     #cgi.escape to handle & characters
            else:                               # no page: yet, so print & discard
                print stripline
        elif stripline[0:4].lower() == "tag:":
            # ...add some more validation...
            sometag = stripline[4:].strip()
            if sometag == "":
                print "Empty tag in " + pageID
            else:
                if sometag not in tagdict:      # add new tags to comic tag list
                    tagdict[sometag] = '-'
                    definedtags += 1
                if sometag in pageTags:         # add unique tags to page tag list
                    print "Duplicate tag in " + pageID
                else:
                    pageTags.append(sometag)
                    tagcount[sometag] += 1
        elif stripline[0:5].lower() == "desc:":
            # this is a description
            if pageID > "":
                pageDesc = stripline[5:]
            else:                               # no page: yet print so print & discard
                print stripline
        elif stripline[0:5].lower() == "note:":
            if pageID > "":
                pageNote = stripline[5:]
            else:                               # no page: yet print so print & discard
                print stripline
        else:
            print "UNKNOWN: " + stripline
    f.close()
    if pageID > "":
        # there is a previous page, so output it
        PageOut (pageID, pageDesc, pageNote, pageTags, pageURL)
    return definedtags, totalpages

def DateCountsOut(tags,pages):
    ''' Write update (i.e. run) time, counts to html file.
    '''
    from datetime import datetime, date, time
    d = datetime.utcnow()
    f = codecs.open(updatefile, mode='w', encoding="utf-8")
    f.write( '<p class="quiet right">updated <time>{0}</time> UTC<br>\n'.format(d.isoformat()[:16]))
    f.write( '{0} pages indexed, {1} tags defined</p>\n'.format(pages, tags))
    f.close()

def TagsOut():
    ''' Writes out the tag & desc index block.

    Chapter structure tags separated from in-comic tags
    Now with added Miracle Markdown processing!
    (hence the codecs)
    '''
    f = codecs.open(listtagfile, mode='w', encoding="utf-8") # taglist
    fch = codecs.open(bookfile, mode='w', encoding="utf-8") #book/chapter list
    for eachkey in sorted(tagdict):
        # separate off chapter id tags
        if eachkey.lower()[:3] == "ch-":
            fch.write( '<p id="{0}" class="tags">'.format(eachkey.lower()))
            fch.write( '<span class="tag {0}">'.format(eachkey.lower()) )
            fch.write( '{0}</span> [{1}] '.format(eachkey, tagcount[eachkey]) )
            # markdown conversion
            marky = markdown.markdown( tagdict[eachkey], extensions=['smartypants'] )
            # strip the unwanted para wrapper for writing
            fch.write( marky[3:-4] )
            fch.write( '</p>\n' )
        else:
            f.write( '<p id="{0}" class="tags">'.format(eachkey.lower()))
            f.write( '<span class="tag {0}">'.format(eachkey.lower()) )
            f.write( '{0}</span> [{1}] '.format(eachkey, tagcount[eachkey]) )
            # markdown conversion
            marky = markdown.markdown( tagdict[eachkey], extensions=['smartypants'] )
            # strip the unwanted para wrapper for writing
            f.write( marky[3:-4] )
            f.write( '</p>\n' )
    f.close()
    fch.close()

def PageOut(pageID, pageDesc, pageNote, pageTags, pageURL):
    '''Write page, tag & description block.'''
    # TODO: look at adding generic urls that the pageid plugs into: can probably do that just by checking for a {0} in the url string
    # TODO: add note: processing (same as desc:)
    f = codecs.open(pagesfile, mode='a', encoding="utf-8")
    f.write( '<p class="comicpage')     # '<p class="comicpage'
    pageTags.sort()
    for tag in pageTags:                # write the page tags as css classes
        f.write(' ')                    # '<p class="comicpage '
        f.write( tag.lower() )                  # '<p class="comicpage tag1 ...'
    f.write( '" id="p{0}">\n'.format( pageID ) )  # '<p class="comicpage tag1" id="pPAGEID">\n'
    f.write('<a href="{0}" target="_blank">p.{1}</a>\n'.format( pageURL, pageID  ) )
    marky = markdown.markdown( pageDesc, extensions=['smartypants'] )    # markdown conversion of the description/comment
    if marky == "":                                                      # strip unwanted markdown para for writing
        pass                                                             # skip on a blank
    else:
        f.write( '<span class="description">{0}</span><br>\n'.format( marky[3:-4] ) )
    # add note: processing here
    # now write the tags as tag blobs
    for tag in pageTags:
        f.write( '<span class="tag {0}">{1}</span>\n'.format( tag.lower(), tag ))
    f.write('</p>\n')
    f.close()

if __name__ == '__main__':
	main()
