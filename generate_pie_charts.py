"""
Author: Sam Ginzburg
Description: This script reads in a blast2go sequence table output of GO Term mappings, and calculates frequencies of GO Terms at specific GO Levels

Example run:
python generate_pie_charts.py [blast2go_file.txt] [GO Level]
"""

import sys
from GeneOntologyLibrary import obo_parser
from GeneOntologyLibrary import go_term as gt

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


def parse_go_terms_by_go(go_counts, go, go_type, term_name):
	if go_type == "molecular function":
		if go_counts[0].get(go) is None:
			go_counts[0][go] = 1
		else:
			go_counts[0][go] += 1

	if go_type == "biological process":
		if go_counts[1].get(go) is None:
			go_counts[1][go] = 1
		else:
			go_counts[1][go] += 1
	if go_type == "cellular component":
		if go_counts[2].get(go) is None:
			go_counts[2][go] = 1
		else:
			go_counts[2][go] += 1


def parse_go_mappped_file(go_counts, string):
	#print (string)
	if ";" in string:
		string = string.split(";") # splits the column by ;
	else:
		string = [string]
	#print("splitstring: " + str(split_string))
	return_list = list()
	for go_term in string:
		go_term = go_term.strip()
		
		if go_term == "-":
			continue

		if "P:" in go_term or "Biological Process:" in go_term:
			go_term = go_term[2:]
			if go_counts[0].get(go_term) is None:
				go_counts[0][go_term] = 1
			else:
				go_counts[0][go_term] += 1
		if "F:" in go_term or "Molecular Function:" in go_term:
			go_term = go_term[2:]
			if go_counts[1].get(go_term) is None:
				go_counts[1][go_term] = 1
			else:
				go_counts[1][go_term] += 1			
		if "C:" in go_term or "Cellular Component:" in go_term:
			go_term = go_term[2:]
			if go_counts[2].get(go_term) is None:
				go_counts[2][go_term] = 1
			else:
				go_counts[2][go_term] += 1
		#print (go_term)
		return_list.append(go_term)
	return return_list
		


"""
def filter_by_level(go_dict, level, parser):
	
	for key in dict(go_dict):
		go_term_object = parser.go_term_by_name_dict.get(key[2:])
		if go_term_object is None:
			print ("None -- error has occured:\t" + key[2:])
			exit()
		else:
			print (key)
			print ("level:\t" + str(go_term_object[0].calculate_level()))
			if go_term_object[0].calculate_level() != int(level):				
				del go_dict[key]
"""


def filter_by_level(go_dict, level, parser, go_dict_type):
	if go_dict_type == "biological_process":
		filtered = [x for x in set(go_dict.keys()) & set([gterm.name for gterm in set(parser.get_biological_process_go_terms_by_level(int(level)))])]
	if go_dict_type == "molecular_function":
		filtered = [x for x in set(go_dict.keys()) & set([gterm.name for gterm in set(parser.get_molecular_function_go_terms_by_level(int(level)))])]
	if go_dict_type == "cellular_component":
		filtered = [x for x in set(go_dict.keys()) & set([gterm.name for gterm in set(parser.get_cellular_component_go_terms_by_level(int(level)))])]
		
	#print ("filtered:\t" + str(filtered))
	ret_dict = dict()
	for key in filtered:
		ret_dict[key] = go_dict[key]
	return ret_dict


def generate_counts(go_dict, parser):
	#print (sum(go_dict.values()))
	#print (len(go_dict))
	for key in dict(go_dict):
		go_term_object = parser.go_term_by_name_dict.get(key)
		if go_term_object is None:
			print ("None -- error has occured:\t" + key)
			exit()
		else:
			for x in range(0, go_dict[key]):
				gt.propogate_go_term(go_term_object[0])
			#exit()

def save_graph(go_dict, chart_type, level, parser):
	fontP = FontProperties()
	fontP.set_size('small')
	# The slices will be ordered and plotted counter-clockwise.
	figure = plt.figure(figsize=(10,10))
	
	labels = go_dict.keys()
	sizes = [parser.go_term_by_name_dict.get(x)[0].encountered_count for x in go_dict]
	#sizes = go_dict.values() 	
	#print (chart_type)
	#print (zip(labels, sizes))
	#print (sum(sizes))
	plt.title('Graph Level %s Pie Chart [%s]' % (level, chart_type))
	total = sum(sizes)
	
	labels = [l+" "+str(float(s)/total * 100)[0:4]+"%  ("+ str(s) + ")" for l,s in zip(labels, sizes)]

	patches, texts = plt.pie(sizes, startangle=90)
	plt.legend(patches, labels, prop = fontP, loc="best")
	# Set aspect ratio to be equal so that pie is drawn as a circle.
	plt.axis('equal')
	#plt.tight_layout()
	#plt.show()



	print (chart_type)
	out = [str(x) + "\t" + str(parser.go_term_by_name_dict.get(x)[0].encountered_count) for x in go_dict]

	for x in out:
		print (x)
	print ("\n")	


	figure.savefig(chart_type+"_level_"+level+'.png',aspect='auto',dpi=100)
	

if __name__ == '__main__':
	args = sys.argv	
	args = args[1:]

	# these dicts store the name of the GO term and the number of times it occurs


	combined = dict()
	biological_process = dict()
	molecular_function = dict()
	cellular_component = dict()

	go_counts = [biological_process, molecular_function, cellular_component]
	
	gene_go_term_dict = dict() # key = SeqName description, value = list of gene ontology terms corresponding to the gene 


	with open(args[0], "r") as f:
		for line in f:
			line = line.split("\t")
			gene_go_term_dict[line[0]] = parse_go_mappped_file(go_counts, line[7])
	
	"""
	# remove all genes with no go terms at all
	for key in dict(gene_go_term_dict):
		if len(gene_go_term_dict[key]) < 1:
			del gene_go_term_dict[key]
	"""

	#print (gene_go_term_dict)
	#print (len(gene_go_term_dict))

	print ("Number of unique biological processes go terms:\t" + str(len(biological_process)))
	print ("Number of unique molecular function go terms:\t" + str(len(molecular_function)))
	print ("Number of unique cellular compontent go terms:\t" + str(len(cellular_component)))
	print ("Number of unique overall go terms:\t" + str(len(biological_process) + len(molecular_function) + len(cellular_component)))


	print ("Number of molecular function go terms:\t" + str(sum(molecular_function.values())))
	print ("Number of biological process go terms:\t" + str(sum(biological_process.values())))
	print ("Number of cellular component go terms:\t" + str(sum(cellular_component.values())))


	parser = obo_parser("go.obo")
	parser.build_obo_file()
	
		

	
	generate_counts(biological_process, parser)
	generate_counts(molecular_function, parser)
	generate_counts(cellular_component, parser)

	#print (sum(biological_process.values()))	
	
	biological_process = filter_by_level(biological_process,args[1], parser, "biological_process")
	molecular_function = filter_by_level(molecular_function,args[1], parser, "molecular_function")
	cellular_component = filter_by_level(cellular_component,args[1], parser, "cellular_component")


	"""
	print (biological_process.keys())
	print(parser.go_term_by_name_dict.get("biological_process")[0].encountered_count)

	print (molecular_function.keys())
	print(parser.go_term_by_name_dict.get("molecular_function")[0].encountered_count)
	"""

	#save_graph(molecular_function, "Molecular Function", str(2), parser)
	

	combined = dict(biological_process)
	combined.update(molecular_function)
	combined.update(cellular_component)


	print ("Number of unique biological processes go terms after filtering by level:\t" + str(len(biological_process)))
	print ("Number of unique molecular function go terms after filtering by level:\t" + str(len(molecular_function)))
	print ("Number of unique cellular compontent go terms after filtering by level:\t" + str(len(cellular_component)))
	print ("Number of unique overall go terms after filtering by level:\t" + str(len(combined)))


	print ("Number of molecular function go terms after filtering by level:\t" + str(sum(molecular_function.values())))
	print ("Number of biological process go terms after filtering by level:\t" + str(sum(biological_process.values())))
	print ("Number of cellular component go terms after filtering by level:\t" + str(sum(cellular_component.values())))
	
	"""
	out = [str(x) + "\t" + str(parser.go_term_by_name_dict.get(x)[0].encountered_count) for x in cellular_component]

	for x in out:
		print (x)
	"""
	
	save_graph(biological_process, "Biological Process", args[1], parser)
	save_graph(molecular_function, "Molecular Function", args[1], parser)
	save_graph(cellular_component, "Cellular Component", args[1], parser)
	save_graph(combined, "All", args[1], parser)
	

	
