import scrapy


class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ['ru.wikipedia.org']
    start_urls = ['https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту']

    def parse(self, response):
        urls = response.css('[id=mw-pages]').css('ul li a')

        for u in urls:
            yield {
                'url': 'https://ru.wikipedia.org' + u.attrib['href'],
                'title': u.attrib['title'],
            }
        next_page = response.css('[id=mw-pages]').xpath("//a[text()='Следующая страница']")
        if next_page is not None:
            next_page_url = 'https://ru.wikipedia.org' + next_page.attrib['href']
            yield response.follow(next_page_url, callback=self.parse)
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