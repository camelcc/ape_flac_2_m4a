import os
import sys
import shutil
import re

def remove_readonly(fn, path, excinfo):
    if fn is os.rmdir:
        os.chmod(path, stat.S_IWRITE)
        os.rmdir(path)
    elif fn is os.remove:
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)

# get the lossless filename from the cue file
def get_filename_from_cue(cue_filepath):
	regex_pattern = re.compile(r"FILE\s*\"(?P<filename>.*)\"")
	for line in open(cue_filepath).readlines():
		matchs = regex_pattern.match(line)
		if matchs:
			return matchs.group('filename')

	return ""

def convert_lossless_in_dir(src, des):
	# check if cue or ape or flac file exists.
	has_cue = False
	has_lossess = False
	cue_files = []
	lossess_files = []
	for file in os.listdir(src):
		filepath = os.path.join(src, file)
		#print filepath
		if os.path.isfile(filepath):
			extension = os.path.splitext(filepath)[1]
			#print "extension = " + extension
			if extension == '.cue':
				if not has_cue:
					has_cue = True
				cue_files.append(filepath)
			elif extension == '.ape' or extension == '.flac' or extension == '.wav':
				if not has_lossess:
					has_lossess = True
				lossess_files.append(filepath)
			else:
				pass
		else:
			pass

	# create output dir
	if has_cue or has_lossess:
		# delete if exist
		if os.path.exists(des):
			shutil.rmtree(des, onerror=remove_readonly)

		# create des
		os.makedirs(des)


	# convert
	#/Applications/XLD.app/Contents/MacOS/XLD --cmdline -c <test.cue> -f alac -o <output.dir> <filename.ape>
	if has_cue:
		# open cue with xld to des
		for file in cue_files:
			lossess_filename = get_filename_from_cue(file)
			if lossess_filename:
				lossess_filepath = os.path.join(src, lossess_filename)
				convert_cue_cmd = "/Applications/XLD.app/Contents/MacOS/XLD --cmdline -c \"" + file + "\" -f alac -o \"" + des + "\" \"" + lossess_filepath + "\""
				print convert_cue_cmd
				os.system(convert_cue_cmd)
			else:
				pass
		return

	#/Applications/XLD.app/Contents/MacOS/XLD --cmdline -f alac -o <output.dir> <filename.ape>
	if has_lossess:
		# open lossess with xld to des
		for file in lossess_files:
			convert_lossless_cmd = "/Applications/XLD.app/Contents/MacOS/XLD --cmdline -f alac -o \"" + des + "\" \"" + file + "\""
			print convert_lossless_cmd
			os.system(convert_lossless_cmd)
		return

def convert_dir(src, des):
	if not os.path.exists(src):
		print src + "doesn't exist, terminate convert process."
		return

	# create destination dir if not exist
	if not os.path.exists(des):
		os.makedirs(des)

	# convert top level dir
	convert_lossless_in_dir(src, des)

	# walk through
	for root, dirs, files in os.walk(src):
		#print root
		for dir in dirs:
			source_dir = os.path.join(root, dir)
			des_dir = source_dir.replace(src, des)
			#print source_dir
			#print des_dir
			convert_lossless_in_dir(source_dir, des_dir)

if __name__ == '__main__':
	src = sys.argv[1]
	des = sys.argv[2]
	#print "input folder = " + src
	#print "output folder =" + des
	convert_dir(src, des)
