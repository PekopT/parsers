{
  "type": "scraper",
  "runtime": "python-2.7",
  "data": {
    "format": "xml",
    "schema": "ohranagovby/schema_org.xml"
  },
  "command": "1> /dev/null scrapy crawl ohranagovby -L CRITICAL
 }