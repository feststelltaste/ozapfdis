import pandas as pd

def read_jdeps_file(path_to_file, fill_dependencies=False):
	'''Imports a Java Dependency Analyzer output

	Command for generating the file set externaly:

		`jdeps -verbose <your_classes_directory> > name_your_file.txt`

	You can then read the `name_your_file.txt` file with this function.

	Parameters:
		- `fill_dependencies`: Lists all target dependencies also on the source side (with empty target and type values).

	The read in output gives you three Series:

		- "from": The full qualified class name of the origin of a dependency relationship
		- "to": The full qualified class name of the target of the dependency relationship
		- "type": "The kind of dependency (different values depending on your own application, good for filtering out some special dependencies)
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

	# some algorithms need to have all target dependencies also on the source side
	if fill_dependencies:
		additional_deps = pd.DataFrame()
		additional_deps['from'] = deps[~deps['to'].isin(deps['from'])]['to'].unique()
		additional_deps['to'] = pd.np.nan
		additional_deps['type'] = pd.np.nan

		deps = pd.concat([deps[['from', 'to', 'type']], additional_deps], ignore_index=True)

	return deps
