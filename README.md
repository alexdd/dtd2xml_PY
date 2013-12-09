dtd2xml_PY
=================

dtd2xml.py generates from a given input DTD usable random XML test data. 
Element occurences, test text parts, language and randomness can 
be configured in dtd2xml.ini. DTD must consist only of ASCII chars.

Options
-------------
							
Options can be set in file dtd2xml.ini. See example .ini file and Python source code.


Prerequisites
-------------

* Windows for executing precompiled binary
* or alternatively Python 2.4 installed on your machine for executing source script


Test-Run
-------

* Configure dtd folder path and root element in dtd2xml.ini
* Be sure that DTD source consists only of ASCII chars
* Execute dtd2xml.exe
* Investigate result files wich have filenames like so <root_elem_name>_<language>.xml


License
-------

dtd2xml_PY is licensed under the GNU General Public License, see file license.txt. 
