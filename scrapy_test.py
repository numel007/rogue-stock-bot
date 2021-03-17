import scrapy

class RepSpider(scrapy.Spider):
    name='RepSpider'

    start_urls=['https://www.repfitness.com/bars-plates']
    item_names = []

    def parse(self, response):
        print('-------------------------------------------')
        links = response.xpath("//ol//strong/a/@href")
        link_list = []
        for link in links:
            link_list.append(link.extract())

        self.item_names.append(response.xpath('//h1[@class="page-title"]/span/text()')[0].extract())


        next_page = response.xpath("//ol//strong/a/@href").get()

        for page in link_list:
            print(f'navigating through link: {next_page}')
            yield scrapy.Request(page, callback=self.parse)

        print('-------------------------------------------')
        print(f'List of items: {self.item_names}')