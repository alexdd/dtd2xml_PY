dtd2xml_PY
=================

dtd2xml.py generates from a given input DTD usable random XML test data. 
Element occurences, test text parts, language and randomness can 
be configured in dtd2xml.ini. DTD must consist only of ASCII chars.

Algorithm
-----------

Steps:

1. Parse DTD as a dictionary with (element,child) key-value-tuples.
2. According to multiplicity of elements and parameters in dtd2xml.ini clone and shuffle elements
3. Also save attributes of elements in dictonary
4. Walk town the graph which is in the first dictonary depth first and write attributes and element tags 


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
* Investigate result files wich have filenames like so &lt;root_elem_name&gt;_&lt;language&gt;.xml


License
-------

dtd2xml_PY is licensed under the GNU General Public License, see file license.txt. 
