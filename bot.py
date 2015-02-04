import time , os , pickle , sys , random , json , urllib2 , tweepy, thread
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

# MAIN TWEET STREAM HANDLER
class MainListner(StreamListener):
	def __init__(self,api,textrc,config):
		self.textrc = textrc
		self.api = api
		self.config = config
		self.ban_words = config["config"]["ban_words"]
		self.ban_user = config["config"]["ban_user"]
		thread.start_new_thread(self.Timed_event_handler,(self.random_tweet,5,))
		for Ad in self.textrc["Ads"]:
			thread.start_new_thread(self.Timed_event_handler,(self.AdHandle,Ad[1],Ad[0],))
		thread.start_new_thread(self.Timed_event_handler,(self.tweetStatus,3,))

	def Timed_event_handler(self,run_f,timeout,addi = None):
		while True:
			if addi == None:
				run_f()
			else:
				run_f(addi)
			time.sleep(3600*timeout)	

	def AdHandle(self,Ad):
		try:
			self.api.update_status(Ad)
			print("Ad Tweet Sent")
		except:
			print("Ad Tweet Failed")

	def tweetStatus(self):
		try:
			self.api.update_status("Listening on "+ 
				' '.join(config["config"]["listners"])
				)
			print("Stauts tweet Sent")
		except:
			print("Stauts tweet Failed")

	def random_tweet(self):
		try:
			self.api.update_status(self.textrc["random_list"][random.randrange(0,len(self.textrc["random_list"])-1)])
			print("Random Tweet Send")
		except:
			print("Random Tweet Failed")
	
	def check_ban(self,t,u):
		if any(word in u for word in self.ban_user):
			return False
		else:
			if any(word in t for word in self.ban_words):
				return False
			else:
				return True 

	def on_data(self, data):
		try:
			t = json.loads(data)
			if self.check_ban(t["text"],t["user"]["screen_name"]):
				self.api.retweet(t["id"])
				print("Retweeted: " + t["user"]["screen_name"])
			else:
				print("Ban "+t["user"]["screen_name"])
		except:
			print("Retweeting Failed")
		return True

	def on_error(self, status):
		print(status)

if __name__ == '__main__':
	# LOADING AND PARSING RESOURCES
	try:
		config = json.loads(open("config.json").read())
		textrc = json.loads(open("textrc.json").read())

	except:
		print("Error loading or pasrsing required files")
		exit()

	# AUTHENTICATING WITH TWITTER
	try:
		auth = tweepy.OAuthHandler(
			config["Auth"]["a_key"],
			config["Auth"]["a_secret"]
			)
		auth.set_access_token(config["Auth"]["a_token"],
			config["Auth"]["aa_secret"]
			)
		api = tweepy.API(auth)
	except:
		print("Auth Fail")
		exit()

	ML = MainListner(api,textrc,config)
	tweetStr = Stream(auth,ML)
	tweetStr.filter(track=config["config"]["listners"])	
