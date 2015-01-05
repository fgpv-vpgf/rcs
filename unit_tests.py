
import json, os, unittest, requests, random, datetime, iso8601, hmac, base64, hashlib

#current assumptions
# flask server is running rcs out of http://127.0.0.1:5000/
# python has requests library installed via pip

class FlaskrTestCase(unittest.TestCase):

	#things to set up at the beginning of unit tests
	def setUp(self):		
		donothing = True
		self.service = 'http://127.0.0.1:5000/'
		self.key = "test-k"
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
		h = hmac.new( str(self.key), msg, digestmod=hashlib.sha256 )
		signature = base64.urlsafe_b64encode( h.digest() ).replace('=','')

		# add sender, authroization and timestamp.
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text", "Sender": self.sender, "Authorization": signature, "TimeStamp": timeStamp}

		#do the put 
		# need to add v1 infront the register
		callResult = requests.put(self.service + 'v1/register/' + testSmallKey, json=payload, headers=headers)
		# callResult = requests.put(self.service + 'v1/register/' + testSmallKey , json=payload, headers=headers)
	
		# do we test anything here?
		print "put result is: " + str(callResult)
	
	
		#do a get on the thing we just put
		
		# configSnippet = requests.get(self.service + "v0.9/docs/en/" + "112233").json()
		# configSnippet = requests.get(self.service + "v1/docs/en/" + testSmallKey).json()
		configSnippet = requests.get(self.service + "v0.9/docs/en/" + testSmallKey).json()
		assert len(configSnippet) == 1
		
		print str(configSnippet)
		
		# print configSnippet[0]['layers']['feature'][0]['id']
		
		#do many more tests here
		
		#test that smallkey is id
		testVal = configSnippet[0]['layers']['feature'][0]['id']
		#testVal = configSnippet[0].layers.feature[0].id
		
		print "testVal:" + testVal
		assert testVal == "rcs." + testSmallKey+ ".en"	
		
if __name__ == '__main__':
	unittest.main()
