{
  "type": "scraper",
  "runtime": "python-2.7",
  "data": {
    "format": "xml",
    "schema": "belinvestbank/schema_org.xml"
  },
  "command": "1> /dev/null scrapy crawl BelinvestbankInfos -L CRITICAL
 }
