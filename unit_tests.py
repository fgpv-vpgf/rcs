
import json, os, unittest, requests, random, datetime, iso8601, hmac, base64, hashlib

#current assumptions
# flask server is running rcs out of http://127.0.0.1:5000/
# python has requests library installed via pip

class FlaskrTestCase(unittest.TestCase):

	#things to set up at the beginning of unit tests
	def setUp(self):		
		donothing = True
		self.service = 'http://127.0.0.1:5000/'
		self.key = "test_-k"
		self.sender = "jstest"
		
		
	#things to release / clean up at end of unit tests
	def tearDown(self):
		donothing = True
	
	#basic test function to prove things are doing stuff
	def test_hello_world(self):
		# testVal = requests.get(self.service + "v1/docs/en/0").json()
		testVal = requests.get(self.service + "v0.9/docs/en/0").json()

		assert len(testVal) == 1
	
	#write a value to the service, then read it back
	def test_read_write(self):
	
		#set up test params
					
		testSmallKey = str(random.randint(100, 1000000))
		
		#payload = json.loads('{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}')
		jsonString = '{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}'
		payload = json.loads('{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}')
		
		#write smallkey for extra sniffing
		print "smallkey " + testSmallKey

		#add timeStamp to the put requeset
		now = datetime.datetime.now( iso8601.iso8601.Utc() )
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
		print "timestamp " + timeStamp
	
		

		# create msg for calculateing HMAC_SHA256
		msg = '/v1/register/'+testSmallKey + self.sender + timeStamp + json.dumps(payload)
		print "msg: " + msg
		
		#generate hash
		# h = hmac.new( str(self.key), msg, digestmod=hashlib.sha256 )
		# signature = base64.urlsafe_b64encode( h.digest() ).replace('=','')

		signature = self.signReqeust(str(self.key), msg)

		print "signature:" + signature
		#signature = self.signReqeust(self.key, msg)

		# add sender, authroization and timestamp.
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": signature, "TimeStamp": timeStamp}

		#do the put 
		# need to add v1 infront the register
		putResponse = requests.put(self.service + 'v1/register/' + testSmallKey, json=payload, headers=headers)
		# callResult = requests.put(self.service + 'v1/register/' + testSmallKey , json=payload, headers=headers)
	
		#make sure success code 201 
		# assert putResponse.status_code == 201
		print "put response "+ str(putResponse)

		# do we test anything here?
		#print "put result is: " + str(callResult)	
		#do a get on the thing we just put
		configSnippet = requests.get(self.service + "v0.9/docs/en/" + testSmallKey).json()
		assert len(configSnippet) == 1
		
		#test that smallkey is id
		testVal = configSnippet[0]['layers']['feature'][0]['id']
		testVal = self.smallkey_from_id(testVal)

		print "testVal:" + testVal
		assert testVal == testSmallKey	

	# Test for put without payload in http put request
	def test_write_no_payload(self):
	
		print "--Test put without payload--"
						
		testSmallKey = str(random.randint(100, 1000000))
		
		#payload = json.loads('{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}')
		jsonString = '{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}'
		payload = json.loads('{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}')
		
		#write smallkey for extra sniffing
		# print "smallkey " + testSmallKey

		#add timeStamp to the put requeset
		now = datetime.datetime.now( iso8601.iso8601.Utc() )
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
		# print "timestamp " + timeStamp		

		# create msg for calculateing HMAC_SHA256
		msg = '/v1/register/'+testSmallKey + self.sender + timeStamp + json.dumps(payload)
		# print "msg: " + msg

		signature = self.signReqeust(str(self.key), msg)

		# print "signature:" + signature
		#signature = self.signReqeust(self.key, msg)

		# add sender, authroization and timestamp.
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": signature, "TimeStamp": timeStamp}

		#do the put 
		# need to add v1 infront the register
		# no payload included
		putResponse = requests.put(self.service + 'v1/register/' + testSmallKey, headers=headers)
		
	
		#make sure success code 201 
		# assert putResponse.status_code == 201
		print "Put response without payload (should be 500): "+ str(putResponse.status_code)
		assert putResponse.status_code == 500
		

	#write multiple keys and read them back
	def test_read_write_multiple_layers(self):

		#get config json 
		key1 = "132456"
		key2 = "123456"
		result = requests.get(self.service + "v0.9/docs/en/"+key1+","+key2).json()

		assert len(result)==2
		testValKey1 = result[0]['layers']['feature'][0]['id']
		testValKey2 = result[1]['layers']['feature'][0]['id']

		testValKey1 = self.smallkey_from_id(testValKey1)
		testValKey2 = self.smallkey_from_id(testValKey2)

		print "testValKey1=" + testValKey1
		print "testValKey2=" + testValKey2

		assert key1 == testValKey1 and key2 == testValKey2

	#test for null
	def test_for_nonexisting_layer(self):
		randomKey = str(random.randint(100, 1000000))

		result = requests.get(self.service + "v0.9/docs/en/"+randomKey).json()

		print "randomKey:" + randomKey

		self.assertIsNone(result[0])

	#test for properties service url, test for en and fr
	# def test_config_property(self):
	# 	assert False

	#test DELETE random key by adding the key, then delete it
	def test_delete(self):
		print "Test Delete"
		#add first
		smallkey = str(random.randint(100, 1000000))
		
		payload = json.loads('{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}')
		
		#write smallkey for extra sniffing
		print "smallkey " + smallkey

		#add timeStamp to the put requeset
		now = datetime.datetime.now( iso8601.iso8601.Utc() )
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')

		msg = '/v1/register/'+smallkey + self.sender + timeStamp + json.dumps(payload)
		print "msg: " + msg
		

		#generate hash
		# h = hmac.new( str(self.key), msg, digestmod=hashlib.sha256 )
		# signature = base64.urlsafe_b64encode( h.digest() ).replace('=','')

		signature = self.signReqeust(str(self.key), msg)

		print "signature:" + signature
		#signature = self.signReqeust(self.key, msg)

		# add sender, authroization and timestamp.
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": signature, "TimeStamp": timeStamp}

		# headers = {"contentType": "application/json; charset=utf-8", "dataType": "text"}

		#do the put 
		# need to add v1 infront the register
		putResponse = requests.put(self.service + 'v1/register/' + smallkey, json=payload, headers=headers)
		
		assert putResponse.status_code == 201
	
		#do a get on the thing we just put
		configSnippet = requests.get(self.service + "v1/docs/en/" + smallkey).json()
		assert len(configSnippet) == 1
		
		#test that smallkey is id
		testVal = configSnippet[0]['layers']['feature'][0]['id']
		#testVal = configSnippet[0].layers.feature[0].id
		testVal = self.smallkey_from_id(testVal)

		print "testVal:" + testVal
		assert testVal == smallkey	
		
		print "Delete:" + smallkey

		delMsg = "/v1/register/"+ smallkey + self.sender + timeStamp

		print "delete message" + delMsg
		delSignature = self.signReqeust(str(self.key), delMsg)

		print "delete signature" + delSignature

		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": delSignature, "TimeStamp": timeStamp}


		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Delete Result:" + str(response)

		#http://docs.python-requests.org/en/latest/api/#requests.Response
		#access the status_code
		assert response.status_code == 204

	#test DELETE for key that does not exist
	def test_delete_non_existing_key(self):
		smallkey="Burlington-Downsview"

		now = datetime.datetime.now( iso8601.iso8601.Utc() )
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')

		delMsg = "/v1/register/"+ smallkey + self.sender + timeStamp
		delSignature = self.signReqeust(str(self.key), delMsg)
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": delSignature, "TimeStamp": timeStamp}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		assert response.status_code == 404

	# ========================Authentication Test===================================
	# Header
	# 1. Test for no signing (No signature)
	# 2. Test for invalid timestamp a. 2 mins+ b. 2 mins-
	# 3. Test for no sender
	# Payload
	# 4. Test for no Payload (Delete)
	# 5. Test for with Payload (Put)
	# 6. Test for invalid msg (invalid msg construction for signing)
	# Key
	# 7. Key must be the same. Test with invalid key
	 
	# 1. Test for no signing
	def test_authorization_no_signing_delete(self):
		smallkey="Burlington-Downsview"

		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text"}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Authorization Test(no signing + delete): Response Code = " + str(response.status_code)

		# Make sure status code is 401
		assert response.status_code == 401

	# 2. Test for invalid timestamp
	# Note: No specific error message for expired timestamp, using  401 status code instead
	# 		Test code for invalid time format is 400
	def test_authorization_expired_timestamp(self):
		print "--Test Expired TimeStamp--"
		smallkey="Burlington-Downsview"

		#set time equals to 15minutes ago
		now = datetime.datetime.now( iso8601.iso8601.Utc() ) - datetime.timedelta(minutes=15)
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')

		delMsg = "/v1/register/"+ smallkey + self.sender + timeStamp
		delSignature = self.signReqeust(str(self.key), delMsg)
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": delSignature, "TimeStamp": timeStamp}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Test timestamp: 15minutes ago " + timeStamp + " Status Code:" + str(response.status_code)
		assert response.status_code == 401
		

	def test_authorization_future_timestamp(self):
		print "--Test Future TimeStamp--"
		smallkey="Burlington-Downsview"

		#set time equals to 15minutes ago
		now = datetime.datetime.now( iso8601.iso8601.Utc() ) + datetime.timedelta(minutes=15)
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')

		delMsg = "/v1/register/"+ smallkey + self.sender + timeStamp
		delSignature = self.signReqeust(str(self.key), delMsg)
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": delSignature, "TimeStamp": timeStamp}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Test timestamp: 15minutes ahead " + timeStamp + " Status Code:" + str(response.status_code)
		assert response.status_code == 401

	# Note failed test: should return 400 according to documentation
	def test_authorization_invalid_timeformat(self):

		print "--Test Invalid Time format--"
		smallkey="Burlington-Downsview"

		#set time equals to 15minutes ago
		now = datetime.datetime.now( iso8601.iso8601.Utc() ) + datetime.timedelta(minutes=15)

		# invalid time format
		timeStamp = now.strftime('%Y-%m-%d %H:%M:%S')

		delMsg = "/v1/register/"+ smallkey + self.sender + timeStamp
		delSignature = self.signReqeust(str(self.key), delMsg)
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": delSignature, "TimeStamp": timeStamp}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Test timestamp invalid time format: " + timeStamp + " Status Code:" + str(response.status_code)
		assert response.status_code == 400
	
	#3. Test for no sender
	def test_authroization_no_sender(self):
		print "--Test No Sender in Header --"
		smallkey="Burlington-Downsview"

		#set time equals to 15minutes ago
		now = datetime.datetime.now( iso8601.iso8601.Utc() ) + datetime.timedelta(minutes=15)

		# invalid time format
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')

		delMsg = "/v1/register/"+ smallkey + self.sender + timeStamp
		delSignature = self.signReqeust(str(self.key), delMsg)
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Authorization": delSignature, "TimeStamp": timeStamp}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Test No Sender in header, Status Code:" + str(response.status_code)
		assert response.status_code == 401
	
	#4. Test without payload (Only testing PUT, for DELETE case, no payload is included
	# see test_write_no_payload

	#5. Test with payload (Should only apply to PUT, because in DELETE, no payload is included)
	# Both cases works. Should add the case for testing PUT without payload


	#6. Test for invalid msg (invalid msg construction for signing)
	# RCS singing require the followin gsg format: "/v1/register/"+ smallkey + self.sender + timeStamp
	# Obivious test, but in case code changed like v1.6 vs v1.7
	def test_invalid_msg_construction(self):

		print "--Test invalid message construction for signing--"
		smallkey="Burlington-Downsview"

		#set time equals to 15minutes ago
		now = datetime.datetime.now( iso8601.iso8601.Utc() ) + datetime.timedelta(minutes=15)
		timeStamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')

		# missing /v1
		delMsg = "/register/"+ smallkey + self.sender + timeStamp
		delSignature = self.signReqeust(str(self.key), delMsg)
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": delSignature, "TimeStamp": timeStamp}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Test invlaid message: missing /v1/ " + timeStamp + " Status Code:" + str(response.status_code)
		assert response.status_code == 401

		# order in correct
		delMsg = "/v1/register/"+ smallkey  + timeStamp + self.sender
		delSignature = self.signReqeust(str(self.key), delMsg)
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": delSignature, "TimeStamp": timeStamp}

		response = requests.delete(self.service + 'v1/register/'+smallkey,  headers=headers)

		print "Test invalid message: incorrect order " + timeStamp + " Status Code:" + str(response.status_code)
		assert response.status_code == 401

	# ========================Helper Functions======================================
	#helper function to strip rcs. and .en from id in the config 
	def smallkey_from_id(self, id):
		smallkey = id.lstrip("rcs.").rstrip(".en")
		return smallkey
	

	#helper function to add Request Signing
	def signReqeust(self, key, msg):
		#generate hash
		h = hmac.new( key, msg, digestmod=hashlib.sha256 )
		signature = base64.urlsafe_b64encode( h.digest() ).replace('=','')
		return signature
		
if __name__ == '__main__':
	unittest.main()
