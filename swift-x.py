
import re
import sys
import argparse

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
	return getattr(config, var) if hasattr(config, var) else None

def replace_var(value, config):
	list = re.findall("\$\((.*?)\)", value)
	for s in list:
		if hasattr(config, s):
			return value.replace('$('+s+')', get_var(s, config))
	return value

def expand_variables(config):
	for key, value in vars(config).items():
		if isinstance(value, str):
			if value.find("$") != -1:
				setattr(config, key, replace_var(value, config))
	return config
			
def parse_config(path):
	myvars = {}
	with open("config.txt") as myfile:
		for line in continuation_lines(myfile):
			name, var = line.partition("=")[::2]
			var = ' '.join(var.split())
			myvars[name.strip()] = var
	config = type("Names", (object,), myvars)
	config = expand_variables(config)

	unresolved = {}
	for key, value in vars(config).items():
		if isinstance(value, str):
			if "$" in value:
				unresolved = add_unresolved_symbols(unresolved, value)

	for key in unresolved.keys():
		print "unresolved symbol " + key

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

	if args.verbose > 0:
		print "swift sources " + str(len(swift_sources))
		for s in swift_sources:
			print s
		print "objc sources " + str(len(objc_sources))
		for s in objc_sources:
			print s

if __name__ == "__main__":
    main()

