
import os
import re
import sys
import argparse

def build_objc_sources(args, config, sources):

	if args.verbose > 0:
		print "objc sources " + str(len(sources))
		for s in sources:
			print s
		print "\n"

	for s in sources:

		# determine target
		target = os.path.splitext(s)[0] + ".o"

		# create the build command and replace unknowns
		if s.endswith(".mm"):
			cc = config['OBJC_C++']
		else:
			cc = config['OBJC']
		cc = replace_var(cc, {'TARGET' : target})
		
		if args.verbose > 0:
			print cc + "\n"

def build_swift_sources(args, config, sources):
	
	if args.verbose > 0:
		print "swift sources " + str(len(sources))
		for s in sources:
			print s
		print "\n"

	for s in sources:
		# swift is weird in that you have to pass all sources when compiling each file
		# so we create a temp array that contains the remaining sources
		remain = ' '.join([v for v in sources if not v == s])

		# determine target
		target = os.path.splitext(s)[0] + ".o"

		# create the build command and replace unknowns
		cc = config['SWIFT_CC']
		cc = replace_var(cc, {'PRIMARY_FILE' : s, 'SWIFT_SOURCES' : remain, 'TARGET' : target})
		
		if args.verbose > 0:
			print cc + "\n"


def add_unresolved_symbols(unresolved, value):
	list = re.findall("\$\((.*?)\)", value)
	for s in list:
		unresolved[s] = s
	return unresolved

def continuation_lines(fin):
    for line in fin:
        line = line.rstrip('\n')
        while line.endswith('\\'):
            line = line[:-1] + next(fin).rstrip('\n')
        yield line

def get_var(var, config):
	return config[var] if var in config else None

def replace_var(value, config):

	#for kv in config.items():
	#	print "replace_var: " + kv[0] + "  =>  " + kv[1]

	list = re.findall("\$\((.*?)\)", value)
	for s in list:
		if s in config:
			value = value.replace('$('+s+')', get_var(s, config))
	return value

def expand_variables(config):
	for kv in config.items():
		if kv[1].find("$") != -1:
			config[kv[0]] = replace_var(kv[1], config)
	return config
			
def parse_config(path):
	config = {}
	with open("config.txt") as myfile:
		for line in continuation_lines(myfile):
			if line.startswith('#') or 0 == len(line):
				continue
			name, var = line.partition("=")[::2]
			var = ' '.join(var.split())
			config[name.strip()] = var
	config = expand_variables(config)

	unresolved = {}
	for kv in config.items():
		if "$" in kv[1]:
			unresolved = add_unresolved_symbols(unresolved, kv[1])

	for key in unresolved.keys():
		print "unresolved symbol " + key
	if len(unresolved):
		print "\n"

	return config

def main():	

	config = parse_config("config.txt")

	swift_sources = []
	objc_sources = []

	parser = argparse.ArgumentParser(description='Build swift and objective-c(++) sources for android')
	parser.add_argument('sources', metavar='S', nargs='+', help='source to compile')
	parser.add_argument('-v', '--verbose', action='count', default=0)
	args = parser.parse_args()

	for a in args.sources:
		if a.endswith(".swift"):
			swift_sources.append(a)
		elif a.endswith(".m") or a.endswith(".mm"):
			objc_sources.append(a)

	build_objc_sources(args, config, objc_sources)
	build_swift_sources(args, config, swift_sources)

if __name__ == "__main__":
    main()

