import scrapy
import re
import unicodedata

params = {"жанр":"genre", "режисс":"director", "стран": "country", "год": "year", "imdb": "imdb"}

class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ['ru.wikipedia.org']
    start_urls = ['https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту']

    def parse(self, response):
        urls = response.css('[id=mw-pages]').css('ul li a')

        for u in urls:
            film_link = 'https://ru.wikipedia.org' + u.attrib['href']
            yield response.follow(film_link, callback=self.parse_film_page)

        next_page = response.css('[id=mw-pages]').xpath("//a[text()='Следующая страница']")
        if next_page is not None:
            next_page_url = 'https://ru.wikipedia.org' + next_page.attrib['href']
            yield response.follow(next_page_url, callback=self.parse)

    def parse_film_page(self, response):
        infobox = response.xpath('//*[contains(@class, "infobox")]//tr')
        film = {'title': response.css("span.mw-page-title-main::text").get()}
        for row in infobox:
            if row.xpath('th'):
                item = row.xpath('th//text()').extract()
                item = [_.strip() for _ in item]
                item = ' '.join(item)
                item = item.replace('\n', '')
                item = unicodedata.normalize("NFKD", item)
                item = re.sub(r' +', ' ', item)
                item = item.strip()
                for pattern in params:
                    if pattern in item.lower():
                        item = params[pattern]

                        if row.xpath('td/div/ul/li'):
                            value = []
                            for li in row.xpath('td/div/ul/li'):
                                value.append(''.join(li.xpath('.//text()').extract()))
                            value = [_.strip() for _ in value if _.strip() and _.replace('\n', '')]
                            value = ', '.join(value)
                        else:
                            value = row.xpath('td//text()').extract()
                            value = [_.strip() for _ in value if _.strip() and _.replace('\n', '')]

                        film[item] = clean_value(value)
        yield film



def clean_value(value):
    value = ' '.join(value)
    value = value.replace('\n', '')
    value = unicodedata.normalize("NFKD", value)
    value = re.sub(r' , ', ', ', value)
    value = re.sub(r' \( ', ' (', value)
    value = re.sub(r' \) ', ') ', value)
    value = re.sub(r' \)', ') ', value)
    value = re.sub(r'\[\d.*\]', ' ', value)
    value = re.sub(r' +', ' ', value)
    return value.strip()