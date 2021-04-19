import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from nbcbcn.items import Article


class nbcbcnSpider(scrapy.Spider):
    name = 'nbcbcn'
    start_urls = ['http://www.nbcb.com.cn/home/important_notices/index.shtml']
    page = 0

    def parse(self, response):
        links = response.xpath('//ul[@id="ul_list"]/li/a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            self.page += 1
            next_page = f'http://www.nbcb.com.cn/home/important_notices/index_{self.page}.shtml'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//p[@class="cms_time"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="cms_cont"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
