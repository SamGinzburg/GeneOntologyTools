import sys

class go_term(object):
	def __init__(self):
		#print ("creating new go term")
		self.set_id(None)
		self.set_name(None)
		self.set_namespace(None)
		self.is_a = list()
		
		
	def set_id(self, id):
		self.id = id
		
	def set_name(self, name):
		self.name = name
		
	def set_namespace(self, namespace):
		self.namespace = namespace
		
	def add_is_a(self, is_a):
		self.is_a.append(is_a)
		
		
	def calculate_level(self, go_term_dict):
		return self.calculate_level_helper(self, go_term_dict, 0)
	
	def calculate_level_helper(self, go_term, go_term_dict, count):
		if len(go_term.is_a) == 0:
			return 1 + count
		else:
			count += 1
			return_list = list()
			for is_a in go_term.is_a:
				return_list.append(self.calculate_level_helper(go_term_dict[is_a[0]], go_term_dict, count))
				return max(return_list)
				

class obo_parser(object):
	def build_obo_file(self):
		print ("Now building %s file" % self.file_name)
		with open(self.file_name, "r") as obo_file:
			current_go_term = None
			for line in obo_file:
				if line.strip() == "[Term]":
					current_go_term = go_term()
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
					if "namespace" == line[:line.index(":")] and not current_go_term is None:
						current_go_term.set_namespace(line[line.index(":")+1:].strip())						
					if "is_a" == line[:line.index(":")] and not current_go_term is None:
						temp = line[line.index(":")+1:].split("!")
						temp[0] = temp[0].strip()
						temp[1] = temp[1].strip()
						current_go_term.add_is_a(temp)	
						
					
		print ("There are %s total go terms" % len(self.go_term_dict))
		
		
	def __init__(self, file_name):
		self.file_name = file_name
		self.subsetdef = list()
		self.go_term_list = list() # list of GO term objects
		self.go_term_dict = dict() # key=GO_id, value=GO term object
		
		#self.build_obo_file()
		
		
if __name__ == "__main__":
	arguments = sys.argv
	
	parser = obo_parser("go.obo")
	parser.build_obo_file()
	
	print (parser.go_term_dict['GO:0044767'].name)
	print ("GO LEVEL:\t %s" % parser.go_term_dict['GO:0044767'].calculate_level(parser.go_term_dict))
	
	"""
	for go_term in parser.go_term_list:
		print (go_term.name)
		print (go_term.id)
		print (go_term.is_a)
		print (len(go_term.is_a))
	"""
