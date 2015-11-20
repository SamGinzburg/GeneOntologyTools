import sys
import re

class go_term(object):
	def __init__(self, ontology_dict):
		#print ("creating new go term")
		self.encountered_count = 0
		self.encountered = False
		self.set_ontology_dict(ontology_dict)	
		self.set_id(None)
		self.set_name(None)
		self.set_namespace(None)
		self.synonyms = None
		self.is_a = list()
		self.has_a = list()



	@staticmethod
	def propogate_go_term(term):
		go_term.propogate_go_term_helper(term)
		go_term.reset_encountered(term)

	@staticmethod
	def propogate_go_term_helper(term):
		if not term.encountered:
			term.encountered = True 		
			term.encountered_count += 1

			#print (term.name)
			#print (term.encountered_count)

			for parent in term.is_a:
				go_term.propogate_go_term_helper(term.ontology_dict.get(parent[0]))	
	
	@staticmethod
	def reset_encountered(term):
		if term.encountered:
			term.encountered = False
			for parent in term.is_a:
				go_term.reset_encountered(term.ontology_dict.get(parent[0]))


	def set_ontology_dict(self, ontology_dict):
		self.ontology_dict = ontology_dict

	def set_id(self, id):
		self.id = id
		
	def set_name(self, name):
		self.name = name
		
	def set_namespace(self, namespace):
		self.namespace = namespace
		
	def add_is_a(self, is_a):
		self.is_a.append(is_a)

	def add_has_a(self, has_a):
		self.has_a.append(has_a)

	def add_synonym(self, synonym):
		if self.synonyms is None:
			self.synonyms = list()
			self.synonyms.append(synonym)
		else:
			self.synonyms.append(synonym)
		
	def calculate_level(self):
		return self.calculate_level_helper(self, 0)

	def calculate_level_helper(self, go_term, count):
		if len(go_term.is_a) == 0:
			return 1 + count
		else:
			count += 1
			return_list = list()
			for is_a in go_term.is_a:
				return_list.append(self.calculate_level_helper(self.ontology_dict[is_a[0]], count))
			return max(return_list)

	def __str__(self):
		return "id:\t" + str(self.id) + "\n" + "name:\t" + str(self.name)	

class obo_parser(object):
	def build_obo_file(self):
		print ("Now building %s file" % self.file_name)
		with open(self.file_name, "r") as obo_file:
			current_go_term = None
			for line in obo_file:
				if line.strip() == "[Term]":
					current_go_term = go_term(self.go_term_dict)
					self.go_term_list.append(current_go_term)
				elif line.strip() == "[Typedef]":
					print ("[TYPEDEF] -- not implemented yet")
					# for parsing [typedef] later on
				elif line.strip() == "":
					#print ("skipping empty line")
					continue
				else:
					#print (line)
					# section to parse header of .obo file
					if "format-version" == line[:line.index(":")] and current_go_term is None:
						self.format_version = line[line.index(":")+1:].strip()
					if "data-version" == line[:line.index(":")]  and current_go_term is None:
						self.data_version = line[line.index(":")+1:].strip()
					if "date" == line[:line.index(":")]  and current_go_term is None:
						self.date = line[line.index(":")+1:].strip()
					if "subsetdef" == line[:line.index(":")]  and current_go_term is None:
						self.subsetdef.append(line[line.index(":")+1:].strip())
						
					# section to parse the actual GO Terms
					if "id" == line[:line.index(":")] and not current_go_term is None:
						current_go_term.set_id(line[line.index(":")+1:].strip())
						self.go_term_dict[current_go_term.id] = current_go_term
					if "name" == line[:line.index(":")] and not current_go_term is None:
						current_go_term.set_name(line[line.index(":")+1:].strip())
						if self.go_term_by_name_dict.get(current_go_term.name) is None:
							self.go_term_by_name_dict[current_go_term.name] = list()
							self.go_term_by_name_dict[current_go_term.name].append(current_go_term)
						else:
							self.go_term_by_name_dict[current_go_term.name].append(current_go_term)		
					if "namespace" == line[:line.index(":")] and not current_go_term is None:
						current_go_term.set_namespace(line[line.index(":")+1:].strip())						
					if "is_a" == line[:line.index(":")] and not current_go_term is None:
						temp = line[line.index(":")+1:].split("!")
						temp[0] = temp[0].strip()
						temp[1] = temp[1].strip()
						current_go_term.add_is_a(temp)
					if "synonym" == line[:line.index(":")] and not current_go_term is None:
						temp = line[line.index(":")+1:]
						match = re.search("\"(.*?)\"", temp).group()[1:-1]
						current_go_term.add_synonym(match)

						if self.go_term_by_name_dict.get(match) is None:
							self.go_term_by_name_dict[match] = list()
							self.go_term_by_name_dict[match].append(current_go_term)
						else:
							self.go_term_by_name_dict[match].append(current_go_term)	
						

		for go_id in self.go_term_dict:
			for is_a_temp in self.go_term_dict.get(go_id).is_a:
				self.go_term_dict.get(is_a_temp[0]).add_has_a(go_id)

		print ("There are %s total go terms" % len(self.go_term_dict))
	"""
	def get_biological_process_go_terms_by_level(self, level):
		# GO:0008150 == the root biological process node in the directed acyclic graph
		
		if level == 1:
			return self.go_term_dict.get("GO:0008150")
		elif level == 2:
			ret_list = list()
			for goterm in self.go_term_dict.get("GO:0008150").has_a:
				ret_list.append(self.go_term_dict.get(goterm))
			return ret_list
		else:
			ret_list = list()
			level -= 2
			for goterm in self.go_term_dict.get("GO:0008150").has_a:
				self.recursive_helper_method_go_terms(self.go_term_dict.get(goterm),level,ret_list)
			return ret_list



	def recursive_helper_method_go_terms(self,term,current_level,ret_list):
		if current_level == 1:
			ret_list = list()
			for goterm in term.has_a:
				ret_list.append(self.go_term_dict.get(goterm))
			print (ret_list)
			return ret_list
		else:
			current_level -= 1
			for goterm in term.has_a:
				self.recursive_helper_method_go_terms(goterm,current_level,ret_list)

	"""

	def get_biological_process_go_terms_by_level(self, level):
		if level == 1:
			ret_list = list()			
			ret_list.append(self.go_term_dict.get("GO:0008150")) # the root biological process node in the directed acyclic graph
			return ret_list
		else:
			ret_list = list()			
			self.recursive_process_helper(level, self.go_term_dict.get("GO:0008150"), ret_list)
			return ret_list
	
	def get_molecular_function_go_terms_by_level(self, level):
		if level == 1:
			ret_list = list()
			ret_list.append(self.go_term_dict.get("GO:0003674")) # the root molecular function node in the directed acyclic graph
			return ret_list
		else:
			ret_list = list()			
			self.recursive_process_helper(level, self.go_term_dict.get("GO:0003674"), ret_list)
			return ret_list

	def get_cellular_component_go_terms_by_level(self, level):
		if level == 1:
			ret_list = list()
			ret_list.append(self.go_term_dict.get("GO:0005575"))
			return ret_list
		else:
			ret_list = list()			
			self.recursive_process_helper(level, self.go_term_dict.get("GO:0005575"), ret_list)
			return ret_list


	"""
	go_term_root = a root go term, like biological_process (must be a go_term object type)
	return_list = the list that will have the result placed into it
	"""
	def recursive_process_helper(self, level, go_term_root, return_list):
		level -= 1
		for goterm in go_term_root.has_a:
			if level == 1:
				return_list.append(self.go_term_dict.get(goterm))
			else:
				self.recursive_process_helper(level, self.go_term_dict.get(goterm), return_list)


	def __init__(self, file_name):
		self.file_name = file_name
		self.subsetdef = list()
		self.go_term_list = list() # list of GO term objects

		self.go_term_dict = dict() # key=GO_id, value=GO term object
		self.go_term_by_name_dict = dict() # key=GO_name, value = list of go objects with the name specified

		"""
		Note the two dicts above are not always the same size, there can be multiple entries of the same name for obsolete go terms		
		"""

		
