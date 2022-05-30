from MongoDBAtlasHelper import MongoDBAtlasHelper

from datetime import datetime
from datetime import timedelta
import time
import configparser
import os
import random
import sys

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.errors import BulkWriteError
from requests.exceptions import RequestException

class ShardTest(object):
	def __init__ (self):	
		self.initProps('./atlas.properties')

	def execute(self, manual):

		test_date = datetime.now()
		test_id = 'shard_test_%s' % test_date.strftime("%Y-%m-%d %H:%M:%S")
		test_results = { '_id' : test_id, 'test_id' : 'shard_test', 'ts' : test_date, 'tag' : 'pov', 'latest' : True }
		test_data = { 'batch_execution_times' : [], 
					  'chunk_counts' : [],
					  'disk_sizes' : [] }
		test_results['test_data'] = test_data
		self.test_results = test_results
		self.test_data = test_data
		# Limit calls to API to get disk size
		self.disk_size_counter = 1
		
		atlas = self.getMongoDBAtlasHelper()
		project_name = self.getTestProjectName()

		# Get project id
		ret = atlas.getProjectByName(project_name)
		project_id = ret['id']
		
		cluster_name = self.getTestClusterName()
		if not manual:
			# Create new cluster
			new_cluster = {  'name' : cluster_name,
					'diskSizeGB' : 160,
					'numShards' : 2,
					'providerSettings' : {
						'providerName' : 'AWS',
						'diskIOPS' : 480,
						'encryptEBSVolume' : True,
						'instanceSizeName' : 'M40',
						'regionName' : self.props['CLUSTER_REGION']
					},
					'replicationFactor' : 3,
					'autoScaling':{'diskGBEnabled' : True },
					"biConnector": {
						"enabled": False,
						"readPreference": "secondary"
					}
				}
				
			try:
				ret = atlas.createCluster(project_id, new_cluster)
			except RuntimeError as ex:
				if not self.cluster_ignore_running:
					raise ex
			
		atlas.waitForClusterRunning(project_id, cluster_name)

		# Connect
		conn_str = self.getConnectionString(atlas, project_name, cluster_name)
		if not self.results_connection_string:
			self.results_connection_string = conn_str
		
		client = MongoClient(conn_str)
		# drop collection
		db = client.get_database('shard_test')
		client.admin.command('enableSharding', 'shard_test')

		# shard collection
		db.drop_collection('test_coll')
		client.admin.command('shardCollection', 'shard_test.test_coll', key={'key': 1})
		coll = db.get_collection('test_coll')

		self.clear_latest_results()
		self.write_test_results(client)
		docs_to_insert_per_batch = 100000
		batch_count = 100
		shard_key_max = 100000

		insert_many_batch_size = 10000
		total_docs_inserted = 0
		
		current_shard_count = 2
		shard_count_sequence = [3, 3, 3, 4, 4, 4, 4, 4, 4]
		shard_count_index = -1
		in_modify_shard = False

		test_start_time = datetime.now()
		done = False
		while not done:
			for i in range(batch_count):
				total_docs_inserted = self.insertDocs(total_docs_inserted, coll, docs_to_insert_per_batch, shard_key_max, insert_many_batch_size)
				if i < batch_count:
					if in_modify_shard:
						state = atlas.getClusterState(project_id, cluster_name)
						self.log_info('Updating shard count %s' % state)
						if state == 'IDLE':
							self.write_test_results(client)
							in_modify_shard = False
					time.sleep(1)
					self.update_disk_size(atlas, project_id, cluster_name)
					self.write_test_results(client)

			# Increase number of shards if running automatically
			if not manual:
				if shard_count_index < len(shard_count_sequence) - 1:
					shard_count_index += 1
					shard_count = shard_count_sequence[shard_count_index]
					if shard_count != current_shard_count:
						current_shard_count = shard_count
						doc = { 'numShards' : current_shard_count  }
						atlas.modifyCluster(project_id, cluster_name, doc )
						self.write_test_results(client)
						in_modify_shard = True
				else:
					done = True

		if not manual:
			self.update_disk_size(atlas, project_id, cluster_name)
			self.write_test_results(client)
			if self.delete_cluster:
				self.log_info('Deleting cluster %s' % cluster_name)
				atlas.deleteCluster(project_id, cluster_name)

		self.log_info('All documents inserted. Please refer to the README for how to use Charts to visualise the output')
		self.log_info('Remember to delete the cluster from the Atlas UI after the chart has been created')

	def insertDocs(self, total_docs_inserted, coll, docs_to_insert, shard_key_max, batch_size):

		# Insert documents
		batch = []
		start_time = datetime.now()

		for i in range(docs_to_insert):
			doc = { 'key' : random.randint(0, shard_key_max) }
			batch.append(doc)

			if len(batch) == batch_size:
				total_docs_inserted += self.do_bulk_insert(coll, batch)
				batch = []

		if len(batch) > 0:
			total_docs_inserted += self.do_bulk_insert(coll, batch)

		end_time = datetime.now()
		diff = end_time - start_time

		self.log_info( 'Inserted %d docs in %.2f seconds, total docs %d' % ( docs_to_insert, diff.total_seconds(), total_docs_inserted ))
		self.test_data['batch_execution_times'].append( { 'ts' : end_time, 'duration' : diff.total_seconds(), 'total_docs' : total_docs_inserted } )
		self.write_test_results()
		return total_docs_inserted

	def do_bulk_insert(self, coll, batch):
		records_inserted = 0
		if len(batch) > 0:
			try:
				coll.insert_many(batch, ordered=False)
				records_inserted += len(batch)
			except BulkWriteError as ex:
				self.log_error(f'do_bulk_insert: BulkWriteError')
				if 'writeErrors' in ex.details:
					writeErrors = ex.details['writeErrors']
					index = 0
					errorsToLog = min(5, len(writeErrors))
					while index < errorsToLog:
						self.log_error(f'\tdo_bulk_insert: BulkWriteError {index}: {writeErrors[index]}')
						index += 1
				else:
					self.log_error(f'\tdo_bulk_insert: BulkWriteError: {ex}')

			except PyMongoError as ex:
				self.log_error(f'\do_bulk_insert: PyMongoError: {ex}')

		return records_inserted

	def clear_latest_results(self):
		client = MongoClient(self.results_connection_string)
		db = client.get_database('test_results')
		db.test_results.update_many({}, { '$unset' : { 'latest' : '' } })

	def write_test_results(self, source_client=None):
		try:
			# Add sharding status
			if source_client:
				chunk_counts = self.get_chunk_counts(source_client)
				if chunk_counts:
					self.test_data['chunk_counts'].append( { 'ts' : datetime.now(), 'chunk_counts' : chunk_counts })

			client = MongoClient(self.results_connection_string)
			db = client.get_database('test_results')
			db.test_results.replace_one( {'_id' : self.test_results['_id']}, self.test_results, upsert=True)
		except PyMongoError as ex:
			self.log_error(f'write_test_results: PyMongoError: {ex}')

	def update_disk_size(self, atlas, project_id, cluster_name):
		try:
			# Limit calls
			self.disk_size_counter -= 1
			if self.disk_size_counter == 0:
				self.disk_size_counter = 5

				self.log_info('Getting total cluster disk size')
				cluster_processes = atlas.getClusterProcesses(project_id, cluster_name)
				if 'REPLICA_PRIMARY' in cluster_processes:
					ids = atlas.clusterProcessesToIds(cluster_processes['REPLICA_PRIMARY'])
					# Add disk size
					measurements = ['DISK_PARTITION_SPACE_USED','DISK_PARTITION_SPACE_FREE']
					ret = atlas.getClusterDiskMeasurements(project_id, ids, measurements, 'PT1M', 'PT2M')

					du_total = self.bytesToGB(self.getTotalValue(ret, 'DISK_PARTITION_SPACE_USED'))
					df_total = self.bytesToGB(self.getTotalValue(ret, 'DISK_PARTITION_SPACE_FREE'))
					disk_total = du_total + df_total
					ret = { 'ts' : datetime.now(), 'disk_total' : disk_total, 'disk_used' : du_total }
					self.test_data['disk_sizes'].append(ret)

		except RequestException as ex:
			self.log_error(f'RequestException: {ex}')


	def get_chunk_counts(self, client):
		pipeline = [
			{
				'$match': {
					'_id': 'shard_test.test_coll'
				}
			}, {
				'$lookup': {
					'from': 'chunks', 
					'localField': 'uuid', 
					'foreignField': 'uuid', 
					'as': 'chunks'
				}
			}, {
				'$unwind': {
					'path': '$chunks'
				}
			}, {
				'$group': {
					'_id': '$chunks.shard', 
					'cnt': {
						'$sum': 1
					}
				}
			}, {
				'$project': {
					'shard': '$_id', 
					'cnt': 1, 
					'_id': 0
				}
			}
		]

		res = list(client.config.collections.aggregate(pipeline))
		chunk_counts = None
		if len(res) > 0:
			chunk_counts = res
		return chunk_counts

	def bytesToGB(self, bytes):
		return bytes / 1073741824

	def getTotalValue(self, ret, metric):
		total = 0
		for id in ret.keys():
			total += self.getLastMeasurementValue(ret[id], metric)

		return total

	def getLastMeasurementValue(self, ret, metric):
		last_value = 0
		measurements = ret['measurements']
		for m in measurements:
			if m['name'] == metric:
				for dp in m['dataPoints']:
					last_value = dp['value']

		return last_value

	def initProps(self, props_file):
		self.props = self.readAtlasProperties(props_file)
		self.api_public_key = self.props['API_PUBLIC_KEY']
		self.api_private_key = self.props['API_PRIVATE_KEY']

		self.results_connection_string = None
		self.delete_cluster = False
		if 'RESULTS_CONNECTION_STRING' in self.props:
			self.results_connection_string = self.props['RESULTS_CONNECTION_STRING'].replace('~', '=')
			self.delete_cluster = True
			self.log_info(f'Writing results back to separate cluster, will delete cluster after run')

		self.cluster_ignore_running = False
		if 'CLUSTER_IGNORE_RUNNING' in self.props:
			self.cluster_ignore_running = self.props['CLUSTER_IGNORE_RUNNING'].lower() == 'true'
			if self.cluster_ignore_running:
				self.log_info('Ignoring running cluster during create')

	def readAtlasProperties(self, props_file):
		config = configparser.RawConfigParser()
		props = {}
		if config.read(props_file):
			for key, value in config.items('Atlas'):
				props[key.upper()] = value
		else:
			raise Exception('Cannot read properties file')

		return props

	def getTestClusterName(self):
		return self.props['CLUSTER_NAME']

	def getTestProjectName(self):
		return self.props['PROJECT_NAME']
		
	def getMongoDBAtlasHelper(self):
		atlas = MongoDBAtlasHelper(self, self.api_public_key, self.api_private_key)
		return atlas

	def getConnectionString(self, atlas, project_name, cluster_name):
		project = atlas.getProjectByName(project_name)
		project_id = project['id']

		ret = atlas.getProjectClusterByName(project_id, cluster_name)
		conn_str = ret['mongoURIWithOptions']
		# Connection string is mongodb://<blah>
		conn_str =  "mongodb://%s:%s@%s" % (self.props['ATLAS_USER'], self.props['ATLAS_PWD'], conn_str[10:])
		conn_str += '&retryWrites=true'
		return conn_str

	def log_info(self, str):
		print('%s: INFO - %s' % (datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), str))

	def log_error(self, str):
		print('%s: ERROR - %s' % (datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), str))
####
# Main
####
if __name__ == '__main__':
	manual = False
	if len(sys.argv) > 1:
		manual = sys.argv[1].lower() == 'manual'
	test = ShardTest()
	test.execute(manual)

	
