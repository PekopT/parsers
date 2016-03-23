{
  "type": "scraper",
  "runtime": "python-2.7",
  "data": {
    "format": "xml",
    "schema": "belorusneft/schema_org.xml"
  },
  "command": "1> /dev/null scrapy crawl belorusneft -L CRITICAL
}