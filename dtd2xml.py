# -*- coding: cp1252 -*-

# Copyright (C) 2007 by Alex Duesel <alex@alex-duesel.de>
# homepage: http://www.mandarine.tv
# See file license.txt for licensing issues
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

''' dtd2xml.py generates from a given input DTD usable random XML test data.
   Element occurences, test text parts. language and randomness can 
   be configured in dtd2xml.ini. DTD must consist only of ASCII chars.
'''

from xml.parsers.xmlproc import dtdparser
from types import ListType
import random
import cgi
import ConfigParser

class configuration(ConfigParser.ConfigParser):
    
    '''parses the configuration file dtd2xml.ini'''
    
    def __init__(self,fname):
        ConfigParser.ConfigParser.__init__(self)
        self.readfp(open(fname))
        
    def excludes(self):    
        
        '''do not consider elements in 'excludes' option'''
        
        return self.get('options','excludes').split(' ')

    def attribute_options(self):    
        
        '''check what attributes should be considered { #REQUIRED | #FIXED | #DEFAULT }'''
        
        return self.get('options','attributes').split(' ')

    def text(self, lang):
        
        '''random text parts of a certain language'''
        
        return self.get('text',lang).split('|')

    def dtd(self):
        
        '''set dtd folder to process'''
        
        return self.get('input','dtd')
        
    def root(self):
        
        '''set the root element'''
        
        return self.get('input','root')

    def xml(self):
        return self.get('output','xml')
                
    def probabilities(self):
        
        '''set probabilities'''
        
        items = self.items("probabilities")
        result = {}
        for item in items:
            result[item[0]] = item[1].split(' ')
        return result

    def textlen(self):
        
        '''set max length of PCDATA text'''
        
        items = self.items("textlength")
        result = {}
        for item in items:
            result[item[0]] = int(item[1])
        return result

    def user_attributes(self):    
        
        '''put predefined values into certain attributes'''
        
        items = self.items("attributes")
        result = {}
        for item in items:
            result[item[0]] = item[1].split(' ')
        return result

class randomdata:
    
    '''generate random data'. see also dtd2xml.ini'''
    
    def __init__(self, config, lang):
        self._sentences = config.text(lang) 
        self._probabilities = config.probabilities()
        self._textlen = config.textlen()
        self._init_stack()
        
    def _init_stack(self):    
        self._stack=list(self._sentences)
        random.shuffle(self._stack)
    
    def sentence(self,name):
        
        '''generate random text in PCDATA'''
        
        try:
            length = self._textlen[name]
        except:
            length = 1
        result = ''
        while len(result) < length:
            s = self._stack[0]
            self._stack=self._stack[1:]
            result+=s+' '
            if not len(self._stack):
                self._init_stack()
        return result
        
    def element(self,name):
        
        '''generate random occurence of elements'''
        
        rand = random.randrange(1000)
        prob = 0
        index = 0
        try:
            problist = self._probabilities[name.lower()]
        except KeyError:
            problist = []
        for value in problist:
            prob += int(value)
            if prob >= rand:
                break
            index+=1
        if index < len(problist):
            return index
        return 0
                
class xmlbuilder:
    
    '''generate and assemble XML structure'''
    
    def __init__(self, config):
        self._config = config
        p = dtdparser.DTDParser()
        c = dtdconsumer()
        p.set_dtd_consumer(c)
        self.__dtd = config.dtd()
        self.__attribute_options = config.attribute_options()
        self.__user_attr = config.user_attributes()
        p.parse_resource(self.__dtd)
        self.__elems = c.dtd
        self.__attributes = c.attributes
        self.__contains_pcdata = c.pcdata_keys
        for e in config.excludes():
            try:
                del self.__elems[e]
            except KeyError:
                pass
        self.__counter = {}
        
    # handle element occurences
         
    def _is_optional(self, content):
        return content[0] == u'|' and not \
                (content[2] == u'*' or content[2] == u'+')
                
    def _is_multiple(self,content):
        return isinstance(content[1],list) and \
                (content[2] == u'+' or content[2] == u'*')

    def _is_flexible(self,content):
        return isinstance(content, tuple)

    def _is_multiple_in_sequence(self,content):
        return (content[0]==',') 
        
    def _is_multiple_atom(self,content):
        return isinstance(content,tuple) and \
                (content[1] == u'+' or content[1] == u'*')
                
    def _is_element(self,content):
        return not(isinstance(content, list) or isinstance(content, tuple))
        
    def _is_known(self,content):
        return content in self.__elems.keys()
        
    def _is_empty(self, content):
        return content == 'EMPTY'
        
    def _is_pcdata(self,name):
        return name in self.__contains_pcdata
        
    # process element tags

    def _start_tag(self, name):
        self.__file.write("<" + name + " " + self._attribute(name) + ">")            
               
    def _end_tag(self, name):
        self.__file.write("</" + name + ">")
        
    def _text_tag(self,name):
        self._start_tag(name)
        self.__file.write(self.__data.sentence(name))
        self._end_tag(name)

    def _element_tag(self,name,content):
        self._start_tag(name)
        self._walk(content)
        self._end_tag(name)
        
    def _empty_tag(self,name):
        self._start_tag(name)
        self._end_tag(name)
        
    def _attribute(self, name):
        
        '''handle attributes and put predefined values into attributes'''
        
        result=''
        done=[]
        if name in self.__attributes.keys():
            for attr in self.__attributes[name]:
                done=0
                if name in self.__user_attr.keys():
                    for a in self.__user_attr[name]:
                        aa = a.split("=")
                        n = aa[0]
                        v = aa[1]
                        if attr[0] == n:
                            result+=n+'="'+v+'" '
                            done=1
                            break
                if not done and attr[2] in self.__attribute_options:
                    if isinstance(attr[1],list):
                        result+=attr[0]+'="'+random.choice(attr[1])+'" '
                    elif attr[1]=='CDATA' and attr[3] != None:
                        result+=attr[0]+'="'+attr[3]+'" '
                    else:
                        result+=attr[0]+'="'+attr[1]+'" '
        return result
                
    def _shuffle(self, content):
        
        '''shuffle content for different xml structure'''
        
        result=[]
        for i in range(len(content)):
            result.append(content[i])
            for j in range(self.__data.element(content[i][0])):
                result.append(content[i])
        random.shuffle(result)
        return result
        
    def _repeat(self,content):
        
        '''repeat elements'''
        
        result=[]
        for i in range(len(content)):
            result.append(content[i])
            if content[i][1] == u'*' or content[i][1] == u'+':                    
                for j in range(self.__data.element(content[i][0])):
                    result.append(content[i])
        return result

    def _repeat_atom(self,content):
        
        '''repeat atomic content'''
        
        tmp = (content[0],'')
        result=[tmp]
        for j in range(self.__data.element(content[0])):
            result.append(tmp)
        return result

    def _walk(self, content):
        
        '''walk down recursively the DTD tree and put some random data'''
        
        if not(self._is_element(content)):
            if self._is_flexible(content):
                if self._is_optional(content):
                    content = random.choice(content[1])
                elif self._is_multiple_in_sequence(content):
                    content = self._repeat(content[1])
                elif self._is_multiple(content):
                    content = self._shuffle(content[1])
                elif self._is_multiple_atom(content):
                    content = self._repeat_atom(content)
            for entry in content:
                self._walk(entry)
        elif self._is_known(content):
            name = content
            self.__counter[name] += 1   
            content = self.__elems[name]
            if self._is_empty(content):
                self._empty_tag(name)
            elif self._is_pcdata(name):
                self._text_tag(name)
            elif name != self.__root and self.__counter[name] < 2:
                self._element_tag(name, content)
                self.__counter[name] = 0

    def write(self,lang):
        
        '''write xml tags'''
        
        self.__root = self._config.root()
        self.__fname=  self.__root + '_'+ lang + '.xml'
        self.__data = randomdata(self._config, lang)
        for k in self.__elems.keys():
            self.__counter[k] = 0
        self.__textcnt = 0
        self.__file = open(self.__fname.replace('/', '\\'), 'w')
        self.__file.write('<?xml version="1.0" encoding="UTF-8"?>')
        self.__file.write('<!DOCTYPE '+self.__root+' SYSTEM '+'"'+self.__dtd+'">')
        self._element_tag(self.__root, self.__elems[self.__root]) 
        self.__file.close()
        
    def write_all(self):
        for item in (self._config.items('text')):
            self.write(item[0])
        
class dtdconsumer(dtdparser.DTDConsumer):
    
    '''parse dtd and put result into dictionary for later processing'''
    
    def __init__(self):
        self.dtd = {}
        self.pcdata_keys = []
        self.attributes = {}
    def set_error_handler(self, err):
        pass
    def dtd_start(self):
        pass
    def dtd_end(self):
        pass
    def new_general_entity(self, name, val):
        pass
    def new_external_entity(self, ent_name, pub_id, sys_id, ndata):
        pass
    def new_parameter_entity(self, name, val):
        pass
    def new_external_pe(self, name, pubid, sysid):
        pass
    def new_notation(self, name, pubid, sysid):
        pass
    def new_element_type(self, elem_name, elem_cont):
        self.dtd[elem_name] = elem_cont
        tup = ('#PCDATA', '')
        if isinstance(elem_cont[1],list):
            if tup in elem_cont[1]:
                self.pcdata_keys.append(elem_name)
    def new_attribute(self, elem, attr, a_type, a_decl, a_def):
        try:
            self.attributes[elem].append((attr, a_type, a_decl, a_def))
        except:
            self.attributes[elem]=[(attr, a_type, a_decl, a_def)]
        pass
    def handle_comment(self, contents):
        pass
    def handle_pi(self, target, data): 
        pass
 
config = configuration('dtd2xml.ini')
t = xmlbuilder(config)
print "dtd2xml.py - version 0.1 [15.08.2007]"
print "copyright (c) www.alex-duesel.de"
t.write_all()