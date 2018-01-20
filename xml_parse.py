import xml.etree.ElementTree as ET
import sys
import os
import re
from neo4j.v1 import GraphDatabase, basic_auth
from config import NEO4J_USER, NEO4J_PWD

DIR = '../linux'
XML_EXT = ('.xml')

def parsexml(filename):

	"""makes neo4j graph from the xml files"""
	driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth(NEO4J_USER, NEO4J_PWD))
	print("driver connected")
	session = driver.session()
	print("got session")
	session.run("MATCH (n) DETACH DELETE n")

	f = session.run("CREATE (f:file {name: {name}, level: {level}, path: {path}})"
                                "RETURN ID(f), f.name, f.level"
                                , name=filename, level=1).single()
	f_id = f['ID(f)']
                # f_name = f['f.name']
                # f_level = f['level']

	tree = ET.parse(filename)
	root = tree.getroot()
	print(root.tag)
	print(root.attrib)

	for child in root:

		print("First child: ", child.tag, child.attrib)

                #for i in root:
                #root[0][1].text

		for child1 in child:
			if child1.tag == 'sectiondef' and (child1.attrib['kind'] == 'var' or child1.attrib['kind'] == 'func'):
				print("Nested: ", child1.tag, child1.attrib)

				en1_id = session.run("MERGE (en:function {name: {en_name}, path: {path}})"
                                            "RETURN ID(en)"
                                            , en_name=child1.tag, path=path).single()['ID(en)']

				session.run("MATCH (f:file), (en:function)"
                                    "WHERE ID(f)={f_id} and ID(en)={en_id}"
                                    "MERGE (f)-[:has]->(en)"
                                    , f_id=f_id, en_id=en1_id)

				for child2 in child1:
					print("Nested Nested: ", child2.tag, child2.attrib)	
					print("name: ", child2.find('name').text)

					en1_id = session.run("MERGE (en:function {name: {en_name}, path: {path}})"
                                            "RETURN ID(en)"
                                            , en_name=child1.tag, path=path).single()['ID(en)']

					session.run("MATCH (f:file), (en:function)"
                                	    "WHERE ID(f)={f_id} and ID(en)={en_id}"
	                                    "MERGE (f)-[:has]->(en)"
	                                    , f_id=f_id, en_id=en1_id)

					for p in child2.findall('param'):
						#if child2.find('param').find('declname'):
						#for n in child2.findall('declname'):
						print("parameters: ", child2.find('param').find('type').text)

						if child2.find('param').find('.//declname'):
							print("name : ", child2.find('param').find('.//declname').text)
						#else:
						#	print("parameters: ", child2.find('param').find('type').text)#, child2.find('param').find('declname').text)
						#print("referencedby: ", )

#       for item in tree.iterfind('sectiondef kind = \'var\'/memberdef'):

#               vartype = item.findtext('type')
#               name = item.findtext('name')


#               print(vartype, " ", name)

        #for  member in root.iter('member'):
        #       print(member.attrib)

	for fact in tree.iter(tag = 'sectiondef'):
		factname = fact.find('kind').text
		if factname == "var":
			for var in fact.iter(tag = 'variable'):
				name = var.find('name').text
				print(name)

if __name__ == "__main__":

	xmlfile = sys.argv[1]
	parsexml(xmlfile)
