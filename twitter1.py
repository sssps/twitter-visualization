from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import credentials
from pykafka import KafkaClient
import json

def get_kafka_client():
    return KafkaClient(hosts='127.0.0.1:9092')

class StdOutListener(StreamListener):
    def on_data(self, data):
        print(data)
        message = json.loads(data)
        if message['place'] is not None:
            client = get_kafka_client()
            topic = client.topics['twitterdata1']
            producer = topic.get_sync_producer()
            producer.produce(data.encode('ascii'))
        return True

    def on_error(self, status):
        print(status)

if __name__ == "__main__":
    auth = OAuthHandler(credentials.API_KEY, credentials.API_SECRET_KEY)
    auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
    listener = StdOutListener()
    stream = Stream(auth, listener)
    # stream.filter(track=['abhi singh'])
    stream.filter(locations=[-180,-90,180,90])
    # stream.filter(locations=[5.0770049095, 47.2982950435, 15.0403900146, 54.9039819757])
