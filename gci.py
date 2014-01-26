#! python
# -*- coding: utf-8 -*-

"""Reads the Misfile/Gunnerkrigg character index and outputs it as html web page components

CONFIGURED FOR MISFILE

data in is tab separated lines of form

pageid
0-NN character tags as single word string
end of line comment preceded by #, may be blank

2010-12-09	Ash	Cover	Emily	#=== Book 14 ===

<p class="ash cover emily"><a href="http://www.misfile.com/?date=2010-12-09" target="_blank">2010-12-09</a><span class="tag">
<a class="tash" onclick="setActiveStyleSheet('ash')">Ash</a>
<a class="tcover" onclick="setActiveStyleSheet('cover')">Cover</a>
<a class="temily" onclick="setActiveStyleSheet('emily')">Emily</a>
</span>
Showing of the Instruments</p>

Assumptions
    input is sorted
    a line starting with ; is a comment
    tag defn format is
        @ \t tagword \t tag defn
    NB tag must be valid as css class

    page entry format is
    pageid \t tag \t [...] # text comment (with embedded markup)
    page can have 0 to several tags
    pageid - something linkable (Gunnerkrigg: pageno, Misfile: pagedate)

Writes 4 page-part files for inclusion in a page body:

    update & counts info
    tags index
    page entries
    Chapter/Book list

"""

import string
import collections
import codecs
import markdown
import argparse

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
# debug
# print "indexfile:   " + indexfile
# print "tagsfile:    " + tagsfile
# print "updatefile:  " + updatefile
# print "listtagfile: " + listtagfile
# print "bookfile:    " + bookfile
# print "pagesfile:   " + pagesfile
#
# junk = raw_input("type return: ")


tagdict = {}	# tags : definitions
pagelist = []	# list of page lines
coverlist = []  # list of pages tagged "cover"
tagcount = collections.Counter()


def main():
    tags = 0
    pages = 0

    tags = TagsIn(tags)
    tags, pages = IndexIn(tags, pages)
    DateCountsOut(tags, pages)
    TagsOut()
    MainPageOut()

def TagsIn(definedtags):
    ''' Read a pure tag source file, count tags, fill dictionary.

    file format:
        tag \t definition
    NB tag must be a valid html class

    Using Codecs now because of Markdown requirements later
    '''
    f = codecs.open(tagsfile, mode='r', encoding="utf-8")
    for line in f:
        field = line.split("\t")
        if line[0:1] == ';':
            # it's a comment
            print line
        else:
            tagdict[field[0]] = field[1]
            definedtags += 1
    f.close()
    return definedtags

def IndexIn(definedtags, totalpages):
    ''' Read the page data, separate elements (tags, pages) into dicts and lists, print & discard comments

    Allows for a mixed tag/page file
    Tags format:
        @ \t tag \t definition
    Page format:
        pageid \t tag \t tag ... #page comment

        Using Codecs now because of Markdown requirements later
    '''

    f = codecs.open(indexfile, mode='r', encoding="utf-8")
    for line in f:
        field = line.split("\t")
        # check for tag definition
        if field[0] == '@':
            tagdict[field[1]] = field[2]
            definedtags += 1
        elif line[0:1] == ';':
            # comment
            print line
        else:
            # look for simple tags to add to the dict - exclude first (page id) & last (page comment) element
            for i in range(1, len(field)-1):
                if field[i] == '':
                    print 'Empty tag: ' + line
                else:
                    tagcount[field[i]] += 1
                    if field[i].lower() == 'cover':
                        # add the page id to the list of covers/chapter starts
                        coverlist.append(field[0])
                    if field[i] not in tagdict:
                        # add an 'undefined' tag
                        tagdict[field[i]] = '-'
            pagelist.append(line)
            totalpages += 1
    f.close()
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

def MainPageOut():
    '''Write page, tag & description block.
    '''

    f = codecs.open(pagesfile, mode='w', encoding="utf-8")
    for line in pagelist:
        field = line.split("\t")
        # field 0 = page id
        # ...     = tags
        # field (last) = page comment
        f.write( '<p class="comicpage')
        for i in range(1, len(field) - 1):
            #
            # write the page tags as css classes
            #
            f.write(' ')
            f.write( field[i].lower() )
            if field[i].lower() == "filler":
                f.write(' quiet') # adds Blueprint's de-emphasised grey class
        f.write( '" id="p{0}">\n'.format( field[0] ) )

        # http://www.misfile.com/?date={0}
        # -or-
        # http://www.gunnerkrigg.com/?p={0}

        f.write ('<a href="http://www.misfile.com/?date={0}" target="_blank">{0}</a>\n'.format( field[0] ) )

        # markdown conversion of the description/comment

        marky = markdown.markdown( field[ len( field ) - 1] [1:], extensions=['smartypants'] )
        # strip unwanted markdown para for writing
        if marky == "":
            pass         # skip on a blank
        else:
            f.write( '{0}<br>\n'.format( marky[3:-4] ) )
        # now write the tags as tag blobs
        for i in range(1, len(field) - 1):
            f.write( '<span class="tag {0}">{1}</span>\n'.format(field[i].lower(), field[i]) )
        f.write( '</p>\n')
    f.close()

if __name__ == '__main__':
	main()
