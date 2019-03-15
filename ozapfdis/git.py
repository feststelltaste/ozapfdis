import pandas as pd
import git
from io import StringIO


def log_numstat(path_to_git_repo):

	meta_data_format_string = "%x09%x09%x09%h%x09%aI%x09%aN"

	# connect to repo
	git_bin = git.Repo(path_to_git_repo).git

	# execute log command
	git_log = git_bin.execute('git log --no-merges --no-renames --numstat --pretty=format:"' + meta_data_format_string + '"')

	# read in the log
	git_log = pd.read_csv(
		StringIO(git_log), 
		sep="\t", 
		header=None,
		names=['additions', 'deletions', 'file', 'sha', 'timestamp', 'author']
	)

	# convert to DataFrame
	commit_data = git_log[['additions', 'deletions', 'file']]\
		.join(git_log[['sha', 'timestamp', 'author']]\
		.fillna(method='ffill'))\
		.dropna()
	
	files = pd.read_csv(StringIO(git_bin.execute('git ls-files')), 
		sep="\n", 
		header=None,
		names=['file'])
		
	commits = commit_data[commit_data['file'].isin(files['file'])].copy()
	commits['additions'] = pd.to_numeric(commits['additions'], errors='coerce')
	commits['deletions'] = pd.to_numeric(commits['deletions'], errors='coerce')
	commits['timestamp'] = pd.to_datetime(commits['timestamp'])

	return commits.reset_index(drop=True)


def ls_files(path_to_git_repo):
	git_bin = git.Repo(path_to_git_repo).git
	git_ls_raw = git_bin.execute('git ls-files')
	return pd.read_csv(StringIO(git_ls_raw), sep="\n", names=['file']).set_index('file')


def log_numstat_existing(path_to_git_repo):

	git_ls = ls_files(path_to_git_repo)
	all_files = log_numstat(path_to_git_repo)
	return all_files.join(git_ls, on='file', how='right').reset_index(drop=True)


def indents_existing(path_to_git_repo, file_extensions):

	repo = path_to_git_repo.replace("git", "")
	file_list = ls_files(repo)
	file_list['path'] = repo + "/" + file_list.index
	file_list['file_extension'] = file_list['path'].str.rsplit(".").str[-1]

	content_dfs = []

	for entry in file_list[file_list['file_extension'].isin(['java'])].iterrows():
		file = entry[0]
		path = entry[1]['path']

		content_df = pd.read_csv(
			path,
			sep='\n',
			skip_blank_lines=False,
			names=['line']
		)

		content_df.insert(0, 'file', file)
		content_dfs.append(content_df)

	content = pd.concat(content_dfs)

	content['file'] = pd.Categorical(content['file'])
	content['file'] = content['file'] \
		.str.replace("\\", "/") \
		.str.replace("\.\./", "")

	content['line'] = content['line'].fillna("")
	FOUR_SPACES = " " * 4
	content['line'] = content['line'].str.replace("\t", FOUR_SPACES)

	content['line_number'] = content.index + 1
	content = content.reset_index(drop=True)

	content['is_comment'] = content['line'].str.match(r'^ *(//|/\*|\*).*')
	content['is_empty'] = content['line'].str.replace(" ", "").str.len() == 0
	content['is_code'] = ~(content['is_comment'] | content['is_empty'])

	code = content[content['is_code']][['file', 'line', 'line_number']].copy().reset_index(drop=True)
	code['indent'] = code['line'].str.len() - code['line'].str.lstrip().str.len()
	return code

def numstat_indents_existing(path_to_git_repo, file_exentions):

	indents = indents_existing(path_to_git_repo, file_exentions)
	indents_per_file = indents.groupby('file').agg({
		'indent' : 'sum',
		'line_number' : 'count'})

	indents_per_file['ratio'] = indents_per_file['indent'] / indents_per_file['line_number']

	log = log_numstat_existing(path_to_git_repo)
	most_changed = log['file'].value_counts()
	df = pd.DataFrame(most_changed)
	df = df.join(indents_per_file, how='right')
	df = df.rename(columns={'file': 'changes', 'line_number' : 'lines', 'indent' : 'indents'})
	df = df.sort_values(by='changes', ascending=False)
	return df
