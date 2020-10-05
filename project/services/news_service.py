from flask import abort, jsonify
from pygooglenews import GoogleNews
import newspaper
from newspaper import news_pool
from bs4 import BeautifulSoup
import time
from ..util import within_date_range, format_date
from ..models import Article, db
class NewsService:

    def __init__(self, language='en', news_urls={'https://www.bbc.co.uk/', "https://www.theguardian.com/uk"}):
        self.language = language
        self.news_urls = news_urls

    def scrape(self, **kwargs):
        start_date = format_date(kwargs.get('start_date'))
        end_date = format_date(kwargs.get('end_date'))
        bodies = kwargs.get('bodies').lower() == 'true'
        company_name = kwargs.get('company_name')
        # news articles related to sepcified company from the GoogleNews package
        google_results = self.scrape_google_news(company_name, start_date, end_date, bodies)
        #news articles related to sepcified company from the newspaper package
        newspaper_results = self.scrape_newspapers(company_name, start_date, end_date, bodies)

        google_results.extend(newspaper_results)
        return google_results


    def scrape_google_news(self, company_name, start_date, end_date, bodies):
        try:
            gn = GoogleNews(lang = self.language, country = 'US')
            news_entries = gn.search(company_name, helper = True, when = None, from_ = start_date, to_ = end_date, proxies=None, scraping_bee=None)
            DATE_SLICE = slice(0,16)
        
            if bodies:
                return [{"headline":entry['title'], "body": BeautifulSoup(entry['summary'], "html.parser").get_text(), "source": entry['link'], "published_date": format_date(entry['published'][DATE_SLICE], to_datetime=True, current_format='%a, %d %b %Y'), "company_name":company_name} for entry in news_entries['entries']]
            
            return [{"headline":entry['title'], "source": entry['link'], "published_date": format_date(entry['published'][DATE_SLICE], to_datetime=True, current_format='%a, %d %b %Y'), "company_name":company_name} for entry in news_entries['entries']]

        except Exception as e:
            abort(400, e)


    def scrape_newspapers(self, company_name, start_date, end_date, bodies=False):

        """ Build a list of the newspapers articles from a given url """
        def build_papers(news_url):
            return newspaper.build(news_url,language=self.language, memoize_articles=False)
        
        """ Return a relevant article matching company name and optional params such as start_date, end_date, bodies """
        def relevant_articles(papers):
            try:
                for article in papers.articles:  
                    """
                        Lets analyse the HTML of the article to inspect the h1 (title) of the article. 
                        Reading documentation of newspaper3k suggests parse() is expensive method so 
                        try to limit overhead and only parse articles with a relevant title.
                    """
                    soup = BeautifulSoup(article.html, "html.parser")
                    title = soup.find('h1').get_text()
                    #If the company name is found wihtin the headline of a news article then parse the article for more information
                    if title and company_name in title.lower():
                        article.parse()
                        if within_date_range(article.publish_date, start_date, end_date):
                            article_dict = {"headline": article.title, "source": article.url, "published_date": article.publish_date, "company_name": company_name}
                            if bodies:
                                article_dict.update({"body": article.text})
                            yield article_dict


            except Exception as e:
                #log the error to a file, continue
                print("Exception:", e)
                pass

        articles = []
        company_name = company_name.lower()

        try:
            print("Downloading papers .....")
            papers = [build_papers(src) for src in self.news_urls]
            print("Papers downloaded", len(papers), papers)
            news_pool.set(papers, threads_per_source=2)
            news_pool.join()

        except Exception as e:
            #should log the error to a file in production then continue
            print("Exception:", e)
            pass

        finally:
            articles.extend([article for p in papers for article in relevant_articles(p)])

        return articles

    def save_articles(self, articles):
        if articles and len(articles) > 0:
            if type(articles) == list:
                try:
                    DATE_SLICE = slice(0,16)
                    db.articles.insert_many([Article(**{**article, **{"published_date": format_date(article['published_date'][DATE_SLICE], True, '%a, %d %b %Y')}}).dict() for article in articles])
                    
                except Exception as e:
                    abort(400, e)

        elif type(articles) == dict:
            try:
                db.articles.insert_one(Article(**articles).dict())
            except Exception as e:
                abort(400, e)
        else:
            abort(400, "Article to save should be of type list or type dict")








