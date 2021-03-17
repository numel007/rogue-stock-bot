import scrapy

class RepSpider(scrapy.Spider):
    name='RepSpider'

    start_urls=['https://www.repfitness.com/bars-plates']

    def parse(self, response):
        print('-------------------------------------------')
        data = response.xpath("//ol//strong/a/@href")
        for item in data:
            print(item.extract())
        print('-------------------------------------------')