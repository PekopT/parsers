{
  "type": "scraper",
  "runtime": "python-2.7",
  "data": {
    "format": "xml",
    "schema": "fsvps/schema_org.xml"
  },
  "command": "1> /dev/null scrapy crawl fsvps -L CRITICAL
}
