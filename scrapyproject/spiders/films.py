import scrapy
import re
import unicodedata

#защита от множественного числа и потери ё
params = {"жанр": "genre", "режисс": "director", "стран": "country", "год": "year", "imdb": "imdb"}

class FilmsSpider(scrapy.Spider):
    name = "films"
    allowed_domains = ['ru.wikipedia.org', 'imdb.com']
    start_urls = ['https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту']

    def parse(self, response):
        urls = response.css('[id=mw-pages]').css('ul li a')

        for u in urls[:10]:
            film_link = 'https://ru.wikipedia.org' + u.attrib['href']
            yield response.follow(film_link, callback=self.parse_film_page)

        # next_page = response.css('[id=mw-pages]').xpath("//a[text()='Следующая страница']")
        # if next_page is not None:
        #     next_page_url = 'https://ru.wikipedia.org' + next_page.attrib['href']
        #     yield response.follow(next_page_url, callback=self.parse)

    def parse_film_page(self, response):
        infobox = response.xpath('//*[contains(@class, "infobox")]//tr')
        film = {'title': response.css("span.mw-page-title-main::text").get()}
        imdb_link = ''
        for row in infobox:
            if row.xpath('th'):
                item = row.xpath('th//text()').extract()
                item = ' '.join([_.strip() for _ in item])
                item = item.replace('\n', '')
                item = unicodedata.normalize("NFKD", item)
                item = re.sub(r' +', ' ', item)
                item = item.strip()
                for pattern in params:
                    if pattern in item.lower():
                        item = params[pattern]

                        if item == 'imdb':
                            imdb_link = row.xpath('td//a').attrib['href']
                            break
                        elif row.xpath('td/div/ul/li'):
                            value = []
                            for li in row.xpath('td/div/ul/li'):
                                value.append(''.join(li.xpath('.//text()').extract()))
                            value = [_.strip() for _ in value]
                            value = ', '.join(value)
                    

                        else:
                            value = row.xpath('td//text()').extract()
                            value = [_.strip() for _ in value]
                            value = ' '.join(value)
                        
                        film[item] = clean_value(value, pattern)
        if not imdb_link:
            yield {**film, "imdb": "not found"}
        else:
            yield response.follow(imdb_link, callback=self.parse_imdb, cb_kwargs=film)

    def parse_imdb(self, response, **cb_kwargs):
        title = response.xpath('//meta[@property="og:title"]/@content').get()
        try_score = re.findall(r"\d\.\d", title)
        score = try_score[0] if try_score else 'not found'
        yield {**response.cb_kwargs, "imdb": score}

def clean_value(value, pattern):
    value = value.replace('\n', '')
    value = unicodedata.normalize("NFKD", value)
    value = re.sub(r' , ', ', ', value)
    value = re.sub(r' \( ', ' (', value)
    value = re.sub(r' \) ', ') ', value)
    value = re.sub(r' \)', ') ', value)
    value = re.sub(r'\[[^\]]*\]', '', value)
    value = re.sub(r' +', ' ', value)
    if pattern=='год':
        try_year = re.findall(r'\d{4}', value)
        value = try_year[0] if try_year else value
    elif pattern == 'жанр':
        value = value.lower()
    return value.strip()