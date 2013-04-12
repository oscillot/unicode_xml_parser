import string
from xml.etree import ElementTree
from xmllib import XMLParser, amp, ref


class UnicodeXMLParser(XMLParser):
    def translate_references(self, data, all=1):
        if not self._XMLParser__translate_attribute_references:
            return data
        i = 0
        while 1:
            res = amp.search(data, i)
            if res is None:
                return data
            s = res.start(0)
            res = ref.match(data, s)
            if res is None:
                self.syntax_error("bogus `&'")
                i = s + 1
                continue
            i = res.end(0)
            str = res.group(1)
            rescan = 0
            if str[0] == '#':
                if str[1] == 'x':
                    str = unichr(int(str[2:], 16))
                else:
                    str = unichr(int(str[1:]))
                if data[i - 1] != ';':
                    self.syntax_error("`;' missing after char reference")
                    i = i-1
            elif all:
                if str in self.entitydefs:
                    str = self.entitydefs[str]
                    rescan = 1
                elif data[i - 1] != ';':
                    self.syntax_error("bogus `&'")
                    i = s + 1 # just past the &
                    continue
                else:
                    self.syntax_error("reference to unknown entity `&%s;'" % str)
                    str = '&' + str + ';'
            elif data[i - 1] != ';':
                self.syntax_error("bogus `&'")
                i = s + 1 # just past the &
                continue

            # when we get here, str contains the translated text and i points
            # to the end of the string that is to be replaced
            data = data[:s] + str + data[i:]
            if rescan:
                i = s
            else:
                i = s + len(str)

    def reset(self):
        self.rawdata = ''
        self.stack = []
        self.nomoretags = 0
        self.literal = 0
        self.lineno = 1
        self._XMLParser__at_start = 1
        self._XMLParser__seen_doctype = None
        self._XMLParser__seen_starttag = 0
        self._XMLParser__use_namespaces = 0
        self._XMLParser__namespaces = {'xml':None}   # xml is implicitly declared
        # backward compatibility hack: if elements not overridden,
        # fill it in ourselves
        if self.elements is UnicodeXMLParser.elements:
            self._XMLParser__fixelements()


class UnicodeTreeBuilder(UnicodeXMLParser):

    def __init__(self, html=0, target=None, encoding=None):
        self.__builder = ElementTree.TreeBuilder()
        if html:
            import htmlentitydefs
            self.entitydefs.update(htmlentitydefs.entitydefs)
        UnicodeXMLParser.__init__(self)

    ##
    # Feeds data to the parser.
    #
    # @param data Encoded data.

    def feed(self, data):
        UnicodeXMLParser.feed(self, data)

    ##
    # Finishes feeding data to the parser.
    #
    # @return An element structure.
    # @defreturn Element

    def close(self):
        UnicodeXMLParser.close(self)
        return self.__builder.close()

    def handle_data(self, data):
        self.__builder.data(data)

    handle_cdata = handle_data

    def unknown_starttag(self, tag, attrs):
        attrib = {}
        for key, value in attrs.items():
            attrib[fixname(key)] = value
        self.__builder.start(fixname(tag), attrib)

    def unknown_endtag(self, tag):
        self.__builder.end(fixname(tag))


def fixname(name, split=string.split):
    # xmllib in 2.0 and later provides limited (and slightly broken)
    # support for XML namespaces.
    if " " not in name:
        return name
    return "{%s}%s" % tuple(split(name, " ", 1))
