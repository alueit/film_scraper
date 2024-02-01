import scrapy


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83']

    def parse(self, response):
        countries = response.xpath('//table//b//@title').extract()

        for country in countries:

            country_url = response.xpath('//table//b').extract()

            yield {'countries': country}

    # def start_requests(self):
    #     URL = self.start_urls[0]
    #     yield scrapy.Request(url=URL, callback=self.response_parser)

    # def response_parser(self, response):
    #     for page in response.css('mw-pages'):
    #         yield page
    #         # yield {
    #         #     'title': response.xpath("/html/body/div[3]/h1/span").extract_first(),
    #         # }
    #     # next_page_link = response.css('li.next a::attr(href)').extract_first()
    #     # if next_page_link:
    #     #     yield response.follow(next_page_link, callback=self.response_parser)