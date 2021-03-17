import scrapy

class RepSpider(scrapy.Spider):
    name='RepSpider'

    start_urls=['https://www.repfitness.com/bars-plates']

    def parse(self, response):
        print('-------------------------------------------')
        links = response.xpath("//ol//strong/a/@href")
        link_list = []
        for link in links:
            link_list.append(link.extract())

        next_page = response.xpath("//ol//strong/a/@href").get()

        for page in link_list:
            print(f'navigating through link: {next_page}')
            yield scrapy.Request(page, callback=self.parse)
        print('-------------------------------------------')