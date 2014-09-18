#!/usr/bin/python
#coding=utf-8

#****************************************************************************
# Copyright (c) 2014 Chukong Technologies Inc.
#
# http://www.cocos2d-x.org
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#****************************************************************************

import os
import re
import sys
import argparse
import subprocess

def execute(args, command, stage):

	if None != args.stage and args.stage != str(stage):
		print "Skipping stage " + str(stage)
		return True

	if args.verbose > 0:
		print "Executing command: " + command

	l = command.split()
	try:
		subprocess.check_output(l, stderr=subprocess.STDOUT)
		return True

	except subprocess.CalledProcessError, e:
		print "Command: " + command + "\n"
		print "Output : " + e.output + "\n"
		return False


def build_objc_sources(args, config, sources):

	if args.verbose > 0 and len(sources):
		print "objc sources " + str(len(sources))
		for s in sources:
			print s

	for s in sources:

		print os.path.basename(s)

		ir_name = os.path.splitext(s)[0] + ".ir"
		obj_name = os.path.splitext(s)[0] + ".o"

		# create the build command and replace unknowns
		# this is the first build step from .m(m) => IR
		if s.endswith(".mm"):
			key = 'OBJC_C++'
		else:
			key = 'OBJC'
		cc = get_var(key, config, {'TARGET' : ir_name, \
			                       'TARGET_FILE' : os.path.basename(ir_name), \
			                       'SOURCE' : s, \
			                       'SOURCE_FILE' : os.path.basename(s)})
		if False == execute(args, cc, 1):
			return False

		# now to convert the IR to a .o
		llc = get_var('ANDROID_LLC', config, {'TARGET' : obj_name, \
						                      'TARGET_FILE' : os.path.basename(obj_name), \
										      'SOURCE' : ir_name, \
										      'SOURCE_FILE' : os.path.basename(ir_name)})
		if False == execute(args, llc, 2):
			return False

	return True


def build_swift_sources(args, config, sources):
	
	if args.verbose > 0 and len(sources):
		print "swift sources " + str(len(sources))
		for s in sources:
			print s

	for s in sources:

		print os.path.basename(s)

		# swift is weird in that you have to pass all sources when compiling each file
		# so we create a temp array that contains the remaining sources
		remain = ' '.join([v for v in sources if not v == s])

		ir_name = os.path.splitext(s)[0] + ".ir"
		obj_name = os.path.splitext(s)[0] + ".o"

		# create the build command and replace unknowns
		cc = get_var('SWIFT_CC', config, {'PRIMARY_FILE' : s, \
										  'SWIFT_SOURCES' : remain, \
										  'TARGET' : ir_name, \
										  'TARGET_FILE' : os.path.basename(ir_name), \
										  'SOURCE' : s, \
										  'SOURCE_FILE' : os.path.basename(s)})		
		if False == execute(args, cc, 1):
			return False

		# now to convert the IR to a .o
		llc = get_var('ANDROID_LLC', config, {'TARGET' : obj_name, \
											  'TARGET_FILE' : os.path.basename(obj_name), \
											  'SOURCE' : ir_name,
											  'SOURCE_FILE' : os.path.basename(ir_name)})
		if False == execute(args, llc, 2):
			return False

	return True


def build_asm_sources(args, config, sources):
	
	if args.verbose > 0 and len(sources):
		print "asm sources " + str(len(sources))
		for s in sources:
			print s

	for s in sources:

		print os.path.basename(s)

		ir_name = os.path.splitext(s)[0] + ".ir"
		obj_name = os.path.splitext(s)[0] + ".o"

		# create the build command and replace unknowns
		asm = get_var('ANDROID_AS', config, {'TARGET' : ir_name, \
										     'TARGET_FILE' : os.path.basename(ir_name), \
										     'SOURCE' : s, \
										     'SOURCE_FILE' : os.path.basename(s)})		
		if False == execute(args, asm, 1):
			return False

		# now to convert the IR to a .o
		llc = get_var('ANDROID_LLC', config, {'TARGET' : obj_name, \
											  'TARGET_FILE' : os.path.basename(obj_name), \
											  'SOURCE' : ir_name,
											  'SOURCE_FILE' : os.path.basename(ir_name)})
		if False == execute(args, llc, 2):
			return False

	return True
	

def build_c_sources(args, config, sources):
	
	if args.verbose > 0 and len(sources):
		print "c sources " + str(len(sources))
		for s in sources:
			print s

	for s in sources:

		print os.path.basename(s)

		ir_name = os.path.splitext(s)[0] + ".ir"
		obj_name = os.path.splitext(s)[0] + ".o"

		if s.endswith(".cpp"):
			key = 'CC++'
		else:
			key = 'CC'

		cc = get_var(key, config, {'TARGET' : ir_name, \
			                       'TARGET_FILE' : os.path.basename(ir_name), \
			                       'SOURCE' : s, \
			                       'SOURCE_FILE' : os.path.basename(s)})
		if False == execute(args, cc, 1):
			return False

		# now to convert the IR to a .o
		llc = get_var('ANDROID_LLC', config, {'TARGET' : obj_name, \
						                      'TARGET_FILE' : os.path.basename(obj_name), \
										      'SOURCE' : ir_name, \
										      'SOURCE_FILE' : os.path.basename(ir_name)})
		if False == execute(args, llc, 2):
			return False

	return True


def link_static_library(args, config, sources):

	objects = []
	for s in sources:
		objects.append("obj/" + os.path.basename(os.path.splitext(s)[0] + ".o"))
	objects = ' '.join(objects)

	if args.verbose > 0:
		print objects

	ld = get_var('ANDROID_LD', config, {'OBJECTS' : objects})

	if False == execute(args, ld, None):
		return False

	return True


def add_unresolved_symbols(config, unresolved, value, root_config=None):
	list = re.findall("\$\((.*?)\)", value)
	if root_config != None:
		intrisics = get_var('INTRINSIC_SYMBOLS', root_config, config)
	else:
		intrisics = get_var('INTRINSIC_SYMBOLS', config)

	for s in list:
		if s not in intrisics:
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
		if not isinstance(v, str): # we only expand strings
			return v
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

	if args.verbose > 0:
		print "Parsing " + path

	config = {}
	with open(path) as myfile:
		for line in continuation_lines(myfile):
			if line.startswith('#') or 0 == len(line):
				continue
			name, var = line.partition("=")[::2]
			var = ' '.join(var.split())
			config[name.strip()] = var

	return config


def main():	

	parser = argparse.ArgumentParser(description='Build swift and objective-c(++) sources for android')
	parser.add_argument('sources', metavar='S', nargs='+', help='source to compile')
	parser.add_argument('-v', '--verbose', action='count', default=0)
	parser.add_argument('-vars', action='count', help='dump expanded variables')
	parser.add_argument('--lib', nargs='?', help='link into static library')
	parser.add_argument('-stage', nargs='?', help='which stage number to run')
	parser.add_argument('-x', nargs='?', help='execute argument after evaluating it')

	args = parser.parse_args()

	config = parse_config(args, os.path.dirname(sys.argv[0]) + '/' + "config.txt")

	local = None
	local_path = os.getcwd() + '/' + "config.txt"
	if os.path.isfile(local_path):
		local  = parse_config(args, local_path)

	if None != local:
		config = dict(config.items() + local.items())

	config['CWD'] = os.getcwd()

	# finally expand variables
	config = expand_variables(args, config)

	if 'INTRINSIC_SYMBOLS' in config:
		config['INTRINSIC_SYMBOLS'] = config['INTRINSIC_SYMBOLS'].split()

	# display unresolved
	unresolved = {}
	for kv in config.items():
		if "$" in kv[1]:
			unresolved = add_unresolved_symbols(config, unresolved, kv[1])
	if len(unresolved):
		for key in unresolved.keys():
			print "unresolved symbol " + key

	# display vars
	if args.vars:
		for kv in config.items():
			print "var: " + kv[0] + "  =>  " + str(kv[1])
		return

	# execute commands
	if args.x:
		temp = config
		temp['command'] = args.x
		temp = expand_variables(args, temp)
		execute(args, temp['command'], None)

	swift_sources = []
	objc_sources = []
	asm_sources = []
	c_sources = []

	for a in args.sources:
		if a.endswith(".swift"):
			swift_sources.append(a)
		elif a.endswith(".m") or a.endswith(".mm"):
			objc_sources.append(a)
		elif a.endswith(".s"):
			asm_sources.append(a)
		elif a.endswith(".c") or a.endswith(".cpp"):
			c_sources.append(a)

	if False == build_objc_sources(args, config, objc_sources):
		return False

	if False == build_swift_sources(args, config, swift_sources):
		return False

	if False == build_asm_sources(args, config, asm_sources):
		return False

	if False == build_c_sources(args, config, c_sources):
		return False

	if args.lib:
		return link_static_library(args, config, args.sources)

if __name__ == "__main__":
    main()

