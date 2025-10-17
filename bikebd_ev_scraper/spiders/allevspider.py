import scrapy
import re
from bikebd_ev_scraper.items import BikeItem


class AllevspiderSpider(scrapy.Spider):
    name = "allevspider"
    allowed_domains = ["www.bikebd.com"]
    start_urls = ["https://www.bikebd.com/all-ev"]

    def parse(self, response):
        bikes = response.css("div.mp-bd-card")
        for bike in bikes:
            bike_href = bike.css("a").attrib["href"]
            model = bike_href.split("/")[-1]
            spec_url = f"https://www.bikebd.com/price/{model}/specifications"
            yield scrapy.Request(spec_url, callback=self.parse_spec_url)
            break

    def parse_spec_url(self, response):
        tables = response.xpath("//table")

        result = {}
        bike_item = BikeItem()


        for tr in tables.xpath(".//tr"):
            key_n_values = []
            for p in tr.xpath(".//td//p[not(.//strong)]"):
                # print(p)
                key = p.xpath(".//text()").get().strip().split(":")[0]
                if key == "":
                    continue
                key = re.sub(r'[^a-zA-Z0-9]+', '_', key.strip()).lower()
                key_n_values.append(key)
            for strong in tr.xpath(".//td//strong"):
                a_text = strong.xpath(".//a//text()").get()
                if a_text and not strong.xpath(".//text()").get().strip():
                    value: str = a_text.strip()
                    if "\n" in value:
                        value = value.split("\n")
                        for i, x in enumerate(value):
                            value[i] = x.strip() + " "
                        value = "".join(value)
                    key_n_values.append(value)
                    continue

                value = strong.xpath(".//text()").get().strip()
                if "\n" in value:
                    value = value.split("\n")
                    for i, x in enumerate(value):
                        value[i] = x.strip() + " "
                    value = "".join(value)
                key_n_values.append(value)
            print(key_n_values)
            try:
                result[key_n_values[0]] = key_n_values[2]
                result[key_n_values[1]] = key_n_values[3]
                bike_item[key_n_values[0]] = key_n_values[2]
                bike_item[key_n_values[1]] = key_n_values[3]
            except IndexError:
                result[key_n_values[0]] = key_n_values[1]
                bike_item[key_n_values[0]] = key_n_values[1]

        print(result)
        yield bike_item
