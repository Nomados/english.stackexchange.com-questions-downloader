# -*- coding: utf-8 -*-
import scrapy
import csv
from time import sleep


# this class implements web spider to extract questions from eglish.stackexchange.com site
class JobsSpider(scrapy.Spider):
    # creating of output file to store data
    outfile = open("output.csv", "w", newline="")
    writer = csv.writer(outfile, delimiter=';')

    name = 'EnglishQuestionsExtractor'  # spider name
    allowed_domains = ['english.stackexchange.com']  # site to work on it
    start_urls = ['https://english.stackexchange.com/questions/']  # we will start from all questions list
    domain_name = "https://" + allowed_domains[0]  # full domain name to be used to download questions

    # here we need to retrieve questions from the page
    def parse(self, response):
        questions = response.xpath("//div[@class='summary']")  # html page has set of links to questions body
        item = {}
        for question in questions:
            # url to the detailed page for the question
            url = self.domain_name + question.xpath("h3/a[@class='question-hyperlink']").attrib[
                'href']  # extracting address from the link
            # sending data to the main extractor to follow the link and save data of the question
            yield scrapy.Request(url, callback=self.detail, meta={'item': item})

        # delay here
        sleep(5)

        # selection the next page of the site
        psel = response.xpath("//span[@class='page-numbers next']/..")  # this is the xpath to the "next" pager button
        lnk = self.domain_name + psel.attrib['href']
        if lnk:
            next_page = response.urljoin(lnk)
            yield scrapy.Request(next_page, callback=self.parse)  # go to the next page

    # question body parsing
    def detail(self, response):
        item = response.meta['item']  # meta is used to pass data. Here we store the link to the question body
        name = response.xpath('//h1/a[@class="question-hyperlink"]/text()').extract()[0]  #
        tags = response.xpath("//div/a[@class='post-tag']/text()").extract()
        tags_str = ', '.join(tags).strip(';')

        # clearning ; as it is used as csv separator
        name = name.strip(';')
        # taking div class question descendant a div with a class 'post-text' but not with ancestor tag aside
        # this tag contains warnings about moving the topic to another subforum (for example from 'english' to 'ell'
        question_text = response.xpath(
            "//div[@class='question']//div[@class='post-text']/descendant::text()[not(ancestor::aside)]").extract()
        question_text = ' '.join(question_text)
        question_text = ' '.join(question_text.split())
        question_text = question_text.strip(';')
        question_text = question_text.strip('""')
        question_text = question_text.strip(';')
        url = response.request.url

        if not "[closed]" in name:  # some questions were marked as "closed" and we filtered them out
            self.writer.writerow([name, tags_str, question_text, url])
        yield item

    def close(self):
        self.outfile.close()
        print("-----Check to see if this is closed-----")
