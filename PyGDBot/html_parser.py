from bs4 import BeautifulSoup
from pyquery import PyQuery as pq


class HtmlParser:
    @staticmethod
    def bs4_parser(html, selector):
        result = None
        try:
            html = BeautifulSoup(html, "lxml")
            result = html.select(selector)
        except Exception as e:
            print(e)
        finally:
            return result

    @staticmethod
    def pyq_parser(html, selector):
        result = None
        try:
            html = pq(html)
            result = html(selector)
        except Exception as e:
            print(e)
        finally:
            return result
