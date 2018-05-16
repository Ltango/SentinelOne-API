
import requests
import json
import pprint
import sys
from util import Utilities
import getpass



# Ltango
# 5/10/2018
# Python 2.7
# SentinelOne API version 1.6

# This is a collection of API requests for SentinelOne that can be built upon further
# the easiest way I've found to navigate systems is by utilizing the internal ip to look 
# up agentIDs which then can be passed through various different functions from the API.
# I'm unsure if the Agent Actions or Machine API requests are functional from sentinelOne
# but we can get by without utilizing them There is also the "passphrase" which can be
# easily obtained through the API but doesnot seem to be important for uninstalling
# agents through the API.
# The most difficult aspect is the inconsistent and wildly constructed json responses
# and learning how to parse through the information to find what you need
baseurl = 'https://company.sentinelone.net'
def main():
	username = 'your_username'
	password = 'your_password'
	APIToken = 'your_API_token'

	s = requests.Session()
	temp = raw_input("Username: ")
	# Bypass that can be implemented if you don't mind your username/password/token
	# hardcoded in plaintext into the script (which is bad practice but useful for testing)
	if temp == 'asdf':
		try:
			#password = getpass.getpass('Password: ')
			login(s, username, password, APIToken)
		except:
			return None
	else:
		username = temp
		password = getpass.getpass('Password: ')
		APIToken = raw_input("APIToken: ")
		try:
			login(s, username, password, APIToken)
		except:
			return None

	s.close()


# simple interface so we don't need to write code to call on different functions everytime
def launchInterface(s,userID):
	while True:
		print '1:  get agent ID:'
		print '2:  get UUID'
		print '3:  decommission Agent (doesn\'t work)'
		print '4:  disconnect Agent from network (don\'t do this to yourself...)'
		print '5:  recommission Agent  (doesn\'t work)'
		print '6:  reconnect Agent to network'
		print '7:  get Agent information'
		print '8:  uninstall SentinelOne from agents'
		print '9:  list users'
		print '10: logout\n'
		print '11: get a user details (by id)'
		print '12: get a user details (by username)'		
		print '13: get a user ID\n'
		raw = raw_input("What would you like to do? (enter valid number): ")
		if raw == '1':
			a = raw_input("Enter Internal IP:")
			print iteratorFindAgentIDByIP(s,a)
		elif raw == '2':
			a = raw_input("Enter Internal IP:")
			print iteratorFindAgentUUIDByIP(s,a)
		elif raw == '3':
			a = raw_input("Enter Internal IP:")
			a = iteratorFindAgentIDByIP(s,a)
			decommissionAgent(s,a)
		elif raw == '4':
			a = raw_input("Enter Internal IP:")
			a = iteratorFindAgentIDByIP(s,a)
			disconnectAgentFromNetwork(s,a)
		elif raw == '5':
			a = raw_input("Enter Internal IP:")
			a = iteratorFindAgentIDByIP(s,a)
			recommissionAgent(s,a)
		elif raw == '6':
			a = raw_input("Enter Internal IP:")
			a = iteratorFindAgentIDByIP(s,a)
			reconnectAgentToNetwork(s,a)
		elif raw == '7':
			a = raw_input("Enter Any number of local IP addresses seperated by comma:")
			b = a.split(",")
			for item in b:
				print getAgentInformation(s,item)
		elif raw == '8':
			a = raw_input("Enter Any number of local IP addresses seperated by comma:")
			b = a.split(",")
			for item in b:
				uninstallAgent(s,iteratorFindAgentIDByIP(s,item))
		elif raw == '9':
			print getAllUsers(s)
		elif raw == '10':
			logout(s)
			break
		elif raw == '11':
			a = raw_input("Enter a users's id: ")
			print getUserDetails(s,a)
		elif raw == '12':
			a = raw_input("Enter a users's username: ")
			print getUserDetails(s,getUserIDFromUsername(s,a))
		elif raw == '13':
			a = raw_input("Enter a Username (case sensitive): ")
			print getUserIDFromUsername(s, a)
		else:
			printError('not a valid input')

# login (with API token)
# API tokens will expire after a couple months and are paired with individual users
def login(s, uname, passw, api_token):
	printLog('Logging in...')
	s.headers.update({'Authorization' : 'APIToken ' + api_token})
	payload = {
		'username' : uname,
		'password' : passw
	}
	r = s.post(baseurl + '/web/api/v1.6/users/login', data = payload)
	if printAndCheckStatusCode(r):
		printSuccess('Success!')
		try:
			userID = getUserIDFromUsername(s, uname)
			print 'Welcome ' + getUserFullName(s, userID)
			print getAPITokenDetails(s, userID)
			launchInterface(s, userID)
		except:
			printError("Coudn't retreive token details")
	elif r.status_code == 400:
		printError('Possible Incorrect Login Information.')
	else:
		printError("Server may be busy")


# fun fact - this will also log you out of the website on the chrome tab
# you have to keep visiting
def logout(s):
	printLog('Logging out...')
	r = s.post(baseurl + '/web/api/v1.6/users/logout')
	if printAndCheckStatusCode(r):
		s.close()
	else:
		printError("failed to logout somehow")

#get an agents pass phrase based on agentID - so far I haven't needed it
def getPassPhrase(s, agentID):
	printLog('Fetching PassPhrase for ' + str(agentID))
	r = s.get(baseurl + '/web/api/v1.6/agents/'+ agentID + '/passphrase')
	if printAndCheckStatusCode(r):
		thePassPhrase = get_all(r.json(), 'passphrase').pop()
		return thePassPhrase
	else:
		printError("failed to fetch pass phrase ")
	
#you can get the UUID from the agentID - don't ask me why there are so many different IDs
def getAgentUUID(s,agentID):
	printLog('Fetching UUID for ' + str(agentID))
	r = s.get(baseurl + '/web/api/v1.6/agents/' + agentID)
	if printAndCheckStatusCode(r):
		agentUUID = get_all(r.json(), 'uuid').pop()
		return agentUUID
	else:
		printError("failed to fetch agent UUID ")

# get a JSON response of all users and apparently everything about them
# this can easily be parsed using get_all() but I've barely needed to use this function
def listUsers(s):
	printLog('listing all users...')
	r = s.get(baseurl + '/web/api/v1.6/users')
	if printAndCheckStatusCode(r):
		print r.json()
	else:
		printError("failed to list all users ")

#get a JSON response of agent applications based on agentID
def getAgentApplications(s, agentID):
	printLog('listing agent applications...')
	r = s.get(baseurl + '/web/api/v1.6/agents/' + agentID + '/applications')
	if printAndCheckStatusCode(r):
		return r.json()
	else:
		printError("failed to list agent applications ")

#gets a JSON response based on the agentUUID 
def getByUUID(s, agentUUID):
	printLog('getting agent by UUID...')
	r = s.get(baseurl + '/web/api/v1.6/agents/by-uuid/' + agentUUID)
	if printAndCheckStatusCode(r):
		print r.json()
	else:
		printError("failed to get agent by UUID ")

#useless base method
def iterator(s):
	printLog('iterator...')
	r = s.get(baseurl + '/web/api/v1.6/agents/iterator')
	if printAndCheckStatusCode(r):
		data = json.loads(r.content)
		print data['data']
	else:
		printError("failed utilize iterator ")

#this should be how we find ids
def iteratorFindByName(s, name):
	printLog('iterator finding by name...')
	r = s.get(baseurl + '/web/api/v1.6/agents/iterator?query=' + name + '&limit=1')
	if printAndCheckStatusCode(r):
		return get_all(r.json(), 'id').pop()
	else:
		printError("failed to find by name ")

# this should be how we find ids (probably more useful b/c ip)
def iteratorFindAgentIDByIP(s, ip):
	printLog('iterator finding ID by IP...')
	r = s.get(baseurl + '/web/api/v1.6/agents/iterator?query=' + ip + '&limit=1')
	if printAndCheckStatusCode(r):
		return get_all(r.json(), 'id').pop()
	else:
		printError("failed to find by IP ")

# not really used since I haven't found a use for UUID's yet
def iteratorFindAgentUUIDByIP(s, ip):
	printLog('iterator UUID finding by IP...')
	r = s.get(baseurl + '/web/api/v1.6/agents/iterator?query=' + ip + '&limit=1')
	if printAndCheckStatusCode(r):
		return get_all(r.json(), 'uuid').pop()
	else:
		printError("failed to find by IP ")

# returns agent information based on ip
def getAgentInformation(s, ip):
	printLog('returning Agent Information...')
	r = s.get(baseurl + '/web/api/v1.6/agents/iterator?query=' + ip + '&limit=1')
	if printAndCheckStatusCode(r):
		machineName = get_all(r.json(), 'computer_name').pop()
		agentID = get_all(r.json(), 'id').pop()
		UUID = get_all(r.json(), 'uuid').pop()
		isDecomissioned = get_all(r.json(), 'is_decommissioned').pop()
		networkStatus = get_all(r.json(), 'network_status').pop()
		strbuilder = '\nmachineName: '+ str(machineName) + '\nip: ' + ip + '\nagentID: '+ str(agentID) + '\nUUID: '+ str(UUID)+ '\nis decommissioned: '+ str(isDecomissioned)+ '\nnetwork status: '+ str(networkStatus)+ '\n'
		return strbuilder
	else:
		printError("failed to find agent information ")

# probably never need to do this again
def getAllAgentID(s):
	printLog('Fetching All agent IDs')
	#r = s.get(baseurl + '/web/api/v1.6/agents?limit=100&skip=300&include_decommissioned=true')
	r = s.get(baseurl + '/web/api/v1.6/agents?limit=100&include_decommissioned=true')
	if printAndCheckStatusCode(r):
		agentID = get_all(r.json(), 'id').pop()
		return agentID
	else:
		printError("failed to fetch agent ID ")

# machines don't exist apparently so this is useless
def getMachineName(s, id):
	printLog('Fetching Machine Name For: ' + id)
	r = s.get(baseurl + '/web/api/v1.6/machines/' + id)
	if printAndCheckStatusCode(r):
		machineName = get_all(r.json(), 'name').pop()
		return machineName
	else:
		printError("failed Fetching Machine Information ")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# machines don't exist apparently
def getNumberofMachines(s):
	printLog('Fetching number of Machines')
	r = s.get(baseurl + '/web/api/v1.6/machines/count')
	if printAndCheckStatusCode(r):
		return r.json()
	else:
		printError("failed Fetching Machine Information ")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# I'm actually not sure if this works or not it is an AGENT ACTION TODO: research that
def updateAgentSoftware(s, machineName):
	printLog('Updating Agents software')
	r = s.post(baseurl + '/web/api/v1.6/agents/update-software?query=' +machineName)
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to update software ")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# HAHA YEPP THAT WORKS PERFECTLY ON THE FIRST TRY i feel dumb not saving everything...
# warning - this turns off the agent's machine based on id
def shutdownAgent(s, id):
	printLog('Updating Agents software')
	r = s.post(baseurl + '/web/api/v1.6/agents/shutdown?id__in=' +id)
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to update software ")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# warning - this restarts the agent's machine based on id
def restartAgent(s, id):
	printLog('Restarting Agents Hardware')
	r = s.post(baseurl + '/web/api/v1.6/agents/'+id+'/restart-machined')
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to restart agents hardware ")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# I uninstalled successfully, unsure of difference between this and decommisioning
def uninstallAgent(s, id):
	printLog('Uninstalling Agent')
	r = s.post(baseurl + '/web/api/v1.6/agents/uninstall?id__in=' +id)
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to uninstall")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# Doesn't seem to do anything
def recommissionAgent(s, id):
	printLog('Recommissioning Agent: '+id)
	r = s.post(baseurl + '/web/api/v1.6/agents/'+id+'/recommission')
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to recommission")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# For when you accidently disconnect an agents machine from the network
def reconnectAgentToNetwork(s, id):
	printLog('Reconnecting Agent to network')
	r = s.post(baseurl + '/web/api/v1.6/agents/'+id+'/connect')
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to reconnect agent to network")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# funny how one letter can add an entirely new method
# doesn't seem to do anything
def decommissionAgent(s, id):
	printLog('Decommissioning Agent: ' + id)
	r = s.post(baseurl + '/web/api/v1.6/agents/'+id+'/decommission')
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to decommission")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# don't do this to yourself or you will not have interwebs - and will need your coworker 
# to reconnect you to the network 
def disconnectAgentFromNetwork(s, id):
	printLog('Deconnecting Agent from network')
	r = s.post(baseurl + '/web/api/v1.6/agents/'+id+'/disconnect')
	if printAndCheckStatusCode(r):
		pass
	else:
		printError("failed to deconnect agent from network")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# returns a giant (but pretty) json dump of all the data of the users on the account
def getAllUsers(s):
	printLog('Listing all Users')
	r = s.get(baseurl + '/web/api/v1.6/users')
	if printAndCheckStatusCode(r):
		return json.dumps(r.json(), indent=4)
	else:
		printError("failed to list users")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# returns the API creation/expiration dates for the user
def getAPITokenDetails(s,userid):
	printLog('Showing API Token Details')
	r = s.get(baseurl + '/web/api/v1.6/users/'+userid+'/api-token-details')
	if printAndCheckStatusCode(r):
		print 'token details:'
		return str(json.dumps(r.json(), indent=4)).translate(None, '}{')
	else:
		printError("failed to show API token details")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# returns all of the details in a pretty json response of the user's details
def getUserDetails(s,userid):
	printLog('Showing User Details')
	r = s.get(baseurl + '/web/api/v1.6/users/'+userid)
	if printAndCheckStatusCode(r):
		return json.dumps(r.json(), indent=4)
	else:
		printError("failed to show user details")
		if r.json() is not none:
			print 'raw json data:' + r.json()

# parses through a json response of user data based on userid to only return the full name
def getUserFullName(s, userid):
	printLog('Showing User Full Name')

	r = s.get(baseurl + '/web/api/v1.6/users/'+userid)
	if printAndCheckStatusCode(r):
		data = r.json()
		name = data["full_name"] 
		return name
	else:
		printError("failed to show user full name")
		if r.json() is not none:
			print 'raw json data:' + r.json()



# Super inefficient but the only way - have to get a json response of every single user
# on the account, parse through it to locate the username, and then print only the userID
# the get_all method will not work for this purpose because it would return other ids
# since 'group' has its own id NAMED id FOR SOME REASON
# would be more efficient if we only called this once and stored the data during the session
# but were not limited on API calls so that's fine
def getUserIDFromUsername(s, usrname):
	printLog('retrieving user ID')
	r = s.get(baseurl + '/web/api/v1.6/users')
	if printAndCheckStatusCode(r):
		data = r.json()
		for item in data:
			if usrname in item["username"]:
				theID = item["id"] 
				return theID
		return None
	else:
		printError("failed to retrieve user ID")
		if r.json() is not none:
			print 'raw json data:' + r.json()


# this is my beautiful recursive search function that returns an array of all instances of a key
# within a json response - Sentinel One has many different types of json inside lists and arrays
# all nested within each other so recursion is the only way to go - and it does have to go through
# the entire json response
# THIS WILL RETURN A LIST EVEN IF IT IS ONLY 1 ITEM FOUND SO YOU MUST POP() TO GET CLEAN INPUT
def get_all(myjson, key):
	recursiveResult = []
	if type(myjson) == str:
		myjson = json.loads(myjson)
	if type(myjson) is dict:
		for jsonkey in myjson:
			if type(myjson[jsonkey]) in (list, dict):
				recursiveResult += get_all(myjson[jsonkey], key)
			elif jsonkey == key:
				recursiveResult.append(str(myjson[jsonkey]))
	elif type(myjson) is list:
		for item in myjson:
			if type(item) in (list, dict):
				recursiveResult += get_all(item, key) 
	return recursiveResult

# based on status code from response; really just makes things green, red, or blue
def printAndCheckStatusCode(r):
	if r.status_code == 200 or r.status_code == 204 or r.status_code == 201:
		printSuccess(str(r))
		return True
	elif r.status_code == 405:
		printError(str(r) + " - may need to change 'post' method to 'get' or vise versa")
	else:
		printError(str(r))
	return False

# put these here from utilities file so we don't need 
# to instatiate every single time we need to print
# basically just makes your log pretty and easier to read
def printSuccess(msg):
	print(Utilities.OKGREEN + "[OK]" + msg + Utilities.ENDC)
def printError(msg):
	print(Utilities.FAIL + "[ERROR]" + msg + Utilities.ENDC + str(sys.exc_info()[0]))
def printException(msg):
	print(Utilities.FAIL + "[EXCEPTION]" + msg + Utilities.ENDC + str(sys.exc_info()[0]))
def printLog(msg):
	print(Utilities.OKBLUE + "[LOG]" + msg + Utilities.ENDC)


# launch main()
if __name__ == "__main__": main()