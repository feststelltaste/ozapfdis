import pandas as pd


def read_jdeps_file(path_to_file, filter_regex=None):
	'''Imports a Java Dependency Analyzer output

	Command for generating the file set externaly:

		`jdeps -verbose <your_classes_directory> > name_your_file.txt`

	You can then read the `name_your_file.txt` file with this function.

	The read in output gives you these three eries:

		- "from": The full qualified class name of the origin of a dependency relationship
		- "to": The full qualified class name of the target of the dependency relationship
		- "type": The type that jdeps associates with the Java source code file
	'''
	deps = pd.read_csv(
		path_to_file,
		names=["raw"],
		sep="\n")

	# class entries begin with three whitespaces
	deps = deps[deps['raw'].str.startswith("   ")]
	# separates the source from the target
	splitted = deps['raw'].str.split("->", n=1, expand=True)
	# remove whitespaces from source
	deps['from'] = splitted[0].str.strip()
	# get the target and the artifact names
	splitted_2 = splitted[1].str.split(" ", n=2)
	deps['to'] = splitted_2.str[1]
	deps['type'] = splitted_2.str[2].str.strip()

	if filter_regex:
		deps = deps[deps['from'].str.contains(filter_regex)]
		deps = deps[deps['to'].str.contains(filter_regex)]
		deps = deps.reset_index(drop=True)

	return deps
