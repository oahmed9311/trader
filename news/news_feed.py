import feedparser
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from threading import Thread
import pandas as pd
import datetime
import time

class NewsFeed:
    _k_summary_limit = 180
    _k_business_links = (
        'http://www.business-standard.com/rss/latest.rss',
        'http://www.huffingtonpost.com/feeds/verticals/business/news.xml',
        'http://feeds.bbci.co.uk/news/video_and_audio/business/rss.xml',
        'http://feeds.bbci.co.uk/news/rss.xml?edition=us',
        'https://ir.thomsonreuters.com/rss/news-releases.xml',
        'http://rss.dw.com/rdf/rss-en-bus',
        )
    _k_tech_links = (
        'http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', 
        'http://feeds.bbci.co.uk/news/video_and_audio/technology/rss.xml',
        'http://feeds.reuters.com/reuters/technologyNews?format=xml', 
        'http://www.techinsider.io/rss',
        )
    
    @staticmethod
    def _feedsToDataframe(feeds):
        columns = ['title', 'link', 'summary', 'published', 'sentiment']
        df = pd.DataFrame(columns=columns)
        r = 0
        sid = SentimentIntensityAnalyzer()
        for feed in feeds:
            for entry in feed.entries:
                if 'published_parsed' in entry:
                    published = datetime.datetime.fromtimestamp(time.mktime(entry['published_parsed']))
                elif 'updated' in entry:
                    published = datetime.datetime.fromtimestamp(time.mktime(entry['updated_parsed']))
                entry['published'] = published
                ss = sid.polarity_scores(entry['summary'])
                sentiment = 0
                if ss['pos'] > 2*ss['neg']: sentiment = 1
                elif ss['neg'] > 2*ss['pos']: sentiment = -1
                entry['sentiment'] = sentiment
                df.loc[r] = [entry[k] for k in columns]
                r += 1
        df.sort_values(by=['published'], inplace=True)
        df = df.reset_index(drop=True)
        return df
    
    @staticmethod
    def get(callback):
        def internalGet(callback):
            rss_links = NewsFeed._k_business_links + NewsFeed._k_tech_links
            feeds = []
            for i in range(len(rss_links)):
                link = rss_links[i]
                try:
                    feed = feedparser.parse(link)
                    feeds.append(feed)
                except:
                    pass
            callback(NewsFeed._feedsToDataframe(feeds))
        thread = Thread(target=internalGet, args=(callback,))
        thread.start()
        
    @staticmethod
    def printDataframe():
        def callback(df):
            print(df)
            print(df.dtypes)
        NewsFeed.get(callback)
        

    
def main():
    NewsFeed.printDataframe()

if __name__ == '__main__':
    main()


    