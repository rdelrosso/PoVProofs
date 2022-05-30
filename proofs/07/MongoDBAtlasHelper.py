import requests
from requests.auth import HTTPDigestAuth
import json

from datetime import datetime
import time

'''
Created on 22 Mar 2019

@author: james.osgood
'''

class MongoDBAtlasHelper(object):
	'''
	Helper for Atlas
	'''
	def __init__(self, parent, api_public_key, api_private_key, log_messages=False):
		
		self.atlas_api_base = "https://cloud.mongodb.com/api/atlas/v1.0"
		self.auth = HTTPDigestAuth(api_public_key, api_private_key)
		self.parent = parent

	def getOrgs(self, log_messages=False):
		# Get orgs
		orgs = self.doRequestGet("%s/orgs" % self.atlas_api_base, log_messages)

		# Get projects
		return orgs["results"]

	def getAllProjects(self, log_messages=False):
		
		# Get groups
		ret = self.doRequestGet("%s/groups" % self.atlas_api_base, log_messages)

		return ret["results"]

	def getProjectByName(self, name, log_messages=False):
		
		# Get groups
		ret = self.doRequestGet("%s/groups/byName/%s" % (self.atlas_api_base, name), log_messages)
		return ret

	def getProjectClusters(self, group_id, log_messages=False):
		# Get clusters
		clusters = self.doRequestGet("%s/groups/%s/clusters" % (self.atlas_api_base, group_id), log_messages)
		return clusters

	def getProjectClusterByName(self, group_id, cluster_name, log_messages=False):
		# Get clusters
		clusters = self.doRequestGet("%s/groups/%s/clusters" % (self.atlas_api_base, group_id), log_messages)

		for cluster in clusters["results"]:
			if cluster['name'] == cluster_name:
				return cluster
		
		return None

	def getProjectEvents(self, group_id, start, end=None, filter=None, log_messages=False):
		# Get events
		url = "%s/groups/%s/events?minDate=%s" % (self.atlas_api_base, group_id, self.formatDateISO8601(start))
		if end:
			url = url + '&maxDate=' + self.formatDateISO8601(end)
		
		if filter:
			for key in filter.keys():
				url = url + '&' + key + '=' + filter[key]

		events = self.doRequestGet(url, log_messages)
		return events["results"]

		# Get metrics
		for cluster_process in cluster_processes:
			url = "%s/groups/%s/processes/%s:%d/measurements?granularity=%s&period=%s&m=%s" % (self.atlas_api_base, group_id, cluster_process['hostname'], cluster_process['port'], granularity, period, measurement)
			ret = self.doRequestGet(url, log_messages)
			cluster_process['measurements'] = ret['measurements'][0]

		return cluster_processes

	def getClusterProcesses(self, group_id, cluster_name, log_messages=False):
		
		cluster_name_lower = cluster_name.lower()
		# Get all processes
		url = "%s/groups/%s/processes" % (self.atlas_api_base, group_id)
		processes = self.doRequestGet(url, log_messages)
		
		# process type -> processes
		cluster_processes = {}
		for process in processes['results']:
			# Remove when https://jira.mongodb.org/servicedesk/customer/portal/13/HELP-18778 is fixed
			if 'userAlias' in process:
				userAlias = process['userAlias']
				if userAlias.startswith(cluster_name_lower):
					type = process['typeName']
					p = None
					if type in cluster_processes:
						p = cluster_processes[type]
					else:
						p = []
						cluster_processes[type] = p

					p.append(process)

		return cluster_processes

	def clusterProcessesToIds(self, process_list):
		ids = []
		for process in process_list:
			ids.append(process['id'])

		return ids

	def getClusterProcessMeasurements(self, group_id, ids, measurement, granularity, period, log_messages=False):

		measurements = {}
		# Get metrics
		for id in ids:
			url = "%s/groups/%s/processes/%s/measurements?granularity=%s&period=%s&m=%s" % (self.atlas_api_base, group_id, id, granularity, period, measurement)
			ret = self.doRequestGet(url, log_messages)
			measurements[id] = ret['measurements'][0]

		return measurements

	def getClusterDiskMeasurements(self, group_id, ids, measurements, granularity, period, log_messages=False):

		ret = {}
		for id in ids:
			# Get disks
			url = "%s/groups/%s/processes/%s/disks" % (self.atlas_api_base, group_id, id)
			disks = self.doRequestGet(url, log_messages)
			for disk in disks['results']:
				partitionName = disk['partitionName']

				# Get measurements
				url = "%s/groups/%s/processes/%s/disks/%s/measurements?granularity=%s&period=%s" % (self.atlas_api_base, group_id, id, partitionName, granularity, period)
				for measurement in measurements:
					url = url + '&m=%s' % measurement
				ret[id] = self.doRequestGet(url, log_messages)

		return ret


	def createCluster(self, group_id, data, log_messages=False):
		# Get all processes
		url = "%s/groups/%s/clusters" % (self.atlas_api_base, group_id)
		self.doRequestPost(url, data, 201, log_messages)

	def modifyCluster(self, group_id, cluster_name, data, log_messages=False):
		# Get all processes
		url = "%s/groups/%s/clusters/%s" % (self.atlas_api_base, group_id, cluster_name)
		self.doRequestPatch(url, data, log_messages=log_messages)

	def getClusterState(self, group_id, cluster_id, log_messages=False):

		# Get cluster state
		cluster = self.doRequestGet("%s/groups/%s/clusters/%s" % (self.atlas_api_base, group_id, cluster_id), log_messages=log_messages)
		# Check state
		state = cluster["stateName"]
		return state

	def waitForClusterRunning(self, group_id, cluster_id, log_messages=False):

		done = False
		while not done:
			# Get cluster state
			state = self.getClusterState(group_id, cluster_id,log_messages=log_messages)
			self.parent.log_info("Cluster state: %s" % state)
			if state == "IDLE":
				done = True
			else:
				time.sleep(1)

	def deleteCluster(self, group_id, cluster_id, log_messages=False):

		self.doRequestDelete("%s/groups/%s/clusters/%s" % (self.atlas_api_base, group_id, cluster_id), log_messages=log_messages)

	def formatDateISO8601(self, date):
		return datetime.strftime(date, '%Y-%m-%dT%H:%M:%SZ')

	def formatAPIObject(self, obj):
		return "%s(%s)" % ( obj["name"], obj["id"] )

	def doRequestGet(self, url, log_messages=False):
		if log_messages:
			self.parent.log_info('GET:%s' % url)
		response = requests.get(url, auth=self.auth)
		if log_messages:
			self.parent.log_info(response.json())
		
		expected_return = 200
		if response.status_code != expected_return:
			raise RuntimeError(response.json())
		else:
			return response.json()

	def doRequestPost(self, url, data, expected_return = 200, log_messages = False):
		if log_messages:
			self.parent.log_info(url)
		response = requests.post(url, auth=self.auth, data=json.dumps(data),headers={'content-type':'application/json', 'accept':'application/json'})
		if log_messages:
			self.parent.log_info(response.json())
		if response.status_code != expected_return:
			raise RuntimeError(response.json())
		else:
			return response.json()

	def doRequestPatch(self, url, data, expected_return = 200, log_messages = False):
		if log_messages:
			self.parent.log_info(url)
		headers = { 'Content-Type' : 'application/json'}
		response = requests.patch(url, auth=self.auth, data=json.dumps(data), headers = headers)
		if log_messages:
			self.parent.log_info(response.json())
		if response.status_code != expected_return:
			raise RuntimeError(response.json())
		else:
			return response.json()

	def doRequestDelete(self, url, expected_return = 202, log_messages = False):
		if log_messages:
			self.parent.log_info(url)
		headers = { 'Content-Type' : 'application/json'}
		response = requests.delete(url, auth=self.auth, headers = headers)
		if log_messages:
			self.parent.log_info(response.json())
		if response.status_code != expected_return:
			self.parent.log_info('API call returned %d, expected %d' % (response.status_code, expected_return))
			raise RuntimeError(response.json())
		else:
			return response.json()
