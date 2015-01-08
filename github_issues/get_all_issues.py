import config
import getpass
import urllib2
import base64
import json
import os

"""
Filter based on the "body" of an issue.
Return True if the issue may be an exception report with stack trace, otherwise False
"""
def filter_body(body):
	body = body.lower()
	if body.find("exception")==-1 and body.find("error")==-1: # Should contain "exception" of "error"
		return False
	if len(body.split("at ") ) <4:  # Should contain "at " more than 3 times
		return False
	return True

if __name__ == '__main__':

	cfg = config.config   # Configuration for username and password
	if "username" not in cfg:
		print "Enter your github username:",
		cfg["username"] = raw_input()
	username = cfg["username"]
	print "username:"+username
	if "password" not in cfg:
		cfg["password"] = getpass.getpass("Enter your github password:")
	password = cfg["password"]	
		
	print "validating...",
	header_authorization = base64.encodestring("%s:%s" %(username,password))[:-1]
	request = urllib2.Request("https://api.github.com/user");
	request.add_header("Authorization", "Basic %s" % header_authorization)
	try:
		result = urllib2.urlopen(request)
		if u"login" in json.loads(result.read()):
			print "[Success]"
		else :
			print "[Error]"
			exit(1)
	except:
		print "[Error]"
		exit(1)

	if "repo_user" not in cfg: #Configuration for repository information
		print "Enter the user of the github repository:",
		cfg["repo_user"] = raw_input()
	if "repo_name" not in cfg:
		print "Enter the name of the repository:",
		cfg["repo_name"] = raw_input()
	repo_user = cfg["repo_user"]
	repo_name  = cfg["repo_name"]
	print "repo info:" + repo_user + " / " + repo_name
   
	folder_path = "data/"+repo_user+"/"+repo_name
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)
	
	file_issues_path = folder_path + "/issues.json" # Get the number of issues
	if not os.path.exists(file_issues_path):
		request = urllib2.Request("https://api.github.com/repos/"+repo_user+"/"+repo_name+"/issues")
		request.add_header("Authorization", "Basic %s" % header_authorization)
		result = urllib2.urlopen(request)
		file_issues = open(file_issues_path, "w")
		file_issues.write(result.read())
		file_issues.close()
	data_issues = json.load(file(file_issues_path))
	number_issues = data_issues[0][u"number"]
	print "Number of issues:%d" % number_issues

	f = open(folder_path+ "/fail.txt", "w")
	f.close()
	
	for i in range(1, number_issues+1): # Fetch issue
		print "Issue %d:" % i ,
		try:
			path = "%s/issues_%d.json" % (folder_path, i)
			if not os.path.exists(path):
				request = urllib2.Request("https://api.github.com/repos/"+repo_user+"/"+repo_name+"/issues/"+str(i))
				request.add_header("Authorization", "Basic %s" % header_authorization)
				result = urllib2.urlopen(request)
				file_issues = open(path, "w")
				file_issues.write(result.read())
				file_issues.close()
				print "Fetched"
			else: print "Cached"
		except:
			print "Failed"
			f = open(folder_path+"/fail.txt", 'a')
			f.write(str(i)+"\n")
			f.close()

	print "Filter the issues:"
	
	f = open(folder_path+"/alternatives.txt", "w")
	for i in range(1, number_issues+1):
		print "Issue %d:" % i,
		path = "%s/issues_%d.json" % (folder_path, i)
		if not os.path.exists(path):
			continue
		issue_info = json.load(file(path))
		body = issue_info[u"body"]
		if filter_body(body):
			print "Yes"
			f.write(str(i) + "\n")
		else:
			print "No"
	f.close()
