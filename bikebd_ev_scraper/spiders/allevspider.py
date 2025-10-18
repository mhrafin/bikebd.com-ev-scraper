import scrapy
import re
from bikebd_ev_scraper.items import BikeItem


class AllevspiderSpider(scrapy.Spider):
    name = "allevspider"
    allowed_domains = ["www.bikebd.com"]
    start_urls = ["https://www.bikebd.com/all-ev"]

    # start_urls = ["https://www.bikebd.com/all-ev?page=3"]

    bike_item = BikeItem()

    def parse(self, response):
        bikes = response.css("div.mp-bd-card")

        for bike in bikes:
            bike_href = bike.css("a").attrib["href"]
            model = bike_href.split("/")[-1]
            spec_url = f"https://www.bikebd.com/price/{model}/specifications"
            self.bike_item["page"] = response.url
            yield scrapy.Request(spec_url, callback=self.parse_spec_url)
            # break
        next_page_href = response.css("ul.pagination li a")[-1].attrib["href"]
        if next_page_href is not None:
            yield response.follow(next_page_href, callback=self.parse)

    def parse_spec_url(self, response):
        def remove_new_line(string):
            if "\n" in string:
                string = string.split("\n")
                for i, x in enumerate(string):
                    string[i] = x.strip() + " "
                string = "".join(string)
            return string

        # tables = response.css("div.main-content").xpath(".//table")
        tables = response.xpath('//div[contains(@class,"spec-scroll-main")]//table')
        # print(tables.getall())

        result = {}

        for tr in tables.xpath(".//tr"):
            key_n_values = []
            for p in tr.xpath(".//td//p[not(.//strong)]"):
                # print(p)
                key = p.xpath(".//text()").get().strip().split(":")[0]
                if key == "":
                    continue
                key = re.sub(r"[^a-zA-Z0-9]+", "_", key.strip()).lower()
                key_n_values.append(key)
            for strong in tr.xpath(".//td//strong"):
                a_text = strong.xpath(".//a//text()").get()
                if a_text and not strong.xpath(".//text()").get().strip():
                    value: str = a_text.strip()
                    value = remove_new_line(value)
                    key_n_values.append(value)
                    continue

                value = strong.xpath(".//text()").get().strip()
                value = remove_new_line(value)
                key_n_values.append(value)
            # print("----------------------------------------------------------------------------------")
            # print(response.url)
            # print(key_n_values)
            try:
                result[key_n_values[0]] = key_n_values[2]
                result[key_n_values[1]] = key_n_values[3]
                self.bike_item[key_n_values[0]] = key_n_values[2]
                self.bike_item[key_n_values[1]] = key_n_values[3]
            except IndexError:
                result[key_n_values[0]] = key_n_values[1]
                self.bike_item[key_n_values[0]] = key_n_values[1]

        # print(result)
        self.bike_item["url"] = response.url
        yield self.bike_item
