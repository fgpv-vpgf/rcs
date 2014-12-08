
import json, os, unittest, requests, random

#current assumptions
# flask server is running rcs out of http://127.0.0.1:5000/
# python has requests library installed via pip

class FlaskrTestCase(unittest.TestCase):

	#things to set up at the beginning of unit tests
	def setUp(self):		
		donothing = True
		self.service = 'http://127.0.0.1:5000/'
		
	#things to release / clean up at end of unit tests
	def tearDown(self):
		donothing = True
	
	#basic test function to prove things are doing stuff
	def test_hello_world(self):
		testVal = requests.get(self.service + "docs/en/0").json()
		assert len(testVal) == 1
	
	#write a value to the service, then read it back
	def test_read_write(self):
	
		#set up test params
					
		testSmallKey = str(random.randint(100, 1000000))
		headers = {"contentType": "application/json; charset=utf-8", "dataType": "text"}
		payload = json.loads('{"version": "1.0.0", "payload_type": "feature", "en": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }, "fr": { "service_url": "http://sncr01wbingsdv1.ncr.int.ec.gc.ca/arcgis/rest/services/RAMP/RAMP_ResearchCentres/MapServer/0" }}')
		
		#write smallkey for extra sniffing
		print "smallkey " + testSmallKey
	
			
		#do the put 
		callResult = requests.put(self.service + 'register/' + testSmallKey, json=payload, headers=headers)
	
		# do we test anything here?
		print "put result is: " + str(callResult)
	
	
		#do a get on the thing we just put
		
		
		configSnippet = requests.get(self.service + "docs/en/" + testSmallKey).json()
		assert len(configSnippet) == 1
		
		print str(configSnippet)
		
		#do many more tests here
		
		#test that smallkey is id
		testVal = configSnippet[0].layers.feature[0].id
		
		assert testVal == testSmallKey
	
		
if __name__ == '__main__':
	unittest.main()
