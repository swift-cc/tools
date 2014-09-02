
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

		# create the build command and replace unknowns
		# this is the first build step from .m(m) => IR
		if s.endswith(".mm"):
			key = 'OBJC_C++'
		else:
			key = 'OBJC'
		cc = get_var(key, config, {'TARGET' : os.path.splitext(s)[0] + ".ir", 'SOURCE' : s})
		print "EXEC: " + cc + "\n"

		# now to convert the IR to a .o
		llc = get_var('ANDROID_LLC', config, {'TARGET' : os.path.splitext(s)[0] + ".o", 'SOURCE' : os.path.splitext(s)[0] + ".ir"})
		print "EXEC: " + llc + "\n"


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

		# create the build command and replace unknowns
		cc = get_var('SWIFT_CC', config, {'PRIMARY_FILE' : s, 'SWIFT_SOURCES' : remain, 'TARGET' : os.path.splitext(s)[0] + ".ir", 'SOURCE' : s})		
		print "EXEC: " + cc + "\n"

		# now to convert the IR to a .o
		llc = get_var('ANDROID_LLC', config, {'TARGET' : os.path.splitext(s)[0] + ".o", 'SOURCE' : os.path.splitext(s)[0] + ".ir"})
		print "EXEC: " + llc + "\n"


def add_unresolved_symbols(config, unresolved, value):
	list = re.findall("\$\((.*?)\)", value)
	for s in list:
		if s not in config['INTRINSIC_SYMBOLS']:
			unresolved[s] = s
	return unresolved

def continuation_lines(fin):
    for line in fin:
        line = line.rstrip('\n')
        while line.endswith('\\'):
            line = line[:-1] + next(fin).rstrip('\n')
        yield line

def get_var(var, config, extra=None):
	if extra != None:
		config = dict(config.items() + extra.items())
	if var in config:
		v = config[var]
		list = re.findall("\$\((.*?)\)", v)
		for s in list:
			if s in config:
				v = v.replace('$('+s+')', get_var(s, config))
		return v
	return var

def expand_variables(args, config):
	for kv in config.items():
		config[kv[0]] = get_var(kv[0], config)
		if args.verbose > 1:
			print "expand_variables: " + kv[0] + "  =>  " + config[kv[0]]
	return config
			
def parse_config(args, path):
	config = {}
	with open("config.txt") as myfile:
		for line in continuation_lines(myfile):
			if line.startswith('#') or 0 == len(line):
				continue
			name, var = line.partition("=")[::2]
			var = ' '.join(var.split())
			config[name.strip()] = var

	config = expand_variables(args, config)

	if args.vars:
		for kv in config.items():
			print "var: " + kv[0] + "  =>  " + kv[1]

	if 'INTRINSIC_SYMBOLS' in config:
		config['INTRINSIC_SYMBOLS'] = config['INTRINSIC_SYMBOLS'].split()

	unresolved = {}
	for kv in config.items():
		if "$" in kv[1]:
			unresolved = add_unresolved_symbols(config, unresolved, kv[1])

	if len(unresolved):
		for key in unresolved.keys():
			print "unresolved symbol " + key

	return config

def main():	

	parser = argparse.ArgumentParser(description='Build swift and objective-c(++) sources for android')
	parser.add_argument('sources', metavar='S', nargs='+', help='source to compile')
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('-vars', action='count', help='dump expanded variables')

	args = parser.parse_args()

	config = parse_config(args, "config.txt")

	swift_sources = []
	objc_sources = []

	for a in args.sources:
		if a.endswith(".swift"):
			swift_sources.append(a)
		elif a.endswith(".m") or a.endswith(".mm"):
			objc_sources.append(a)

	build_objc_sources(args, config, objc_sources)
	build_swift_sources(args, config, swift_sources)

if __name__ == "__main__":
    main()

