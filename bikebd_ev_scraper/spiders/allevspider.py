import scrapy


class AllevspiderSpider(scrapy.Spider):
    name = "allevspider"
    allowed_domains = ["www.bikebd.com"]
    start_urls = ["https://www.bikebd.com/all-ev"]

    def parse(self, response):
        pass
