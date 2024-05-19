import scrapy


class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["autoria.comautoria"]
    start_urls = ["https://autoria.comautoria"]

    def parse(self, response):
        pass
