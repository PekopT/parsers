import StringIO

file = open("fsvps/schema_org.xml", "rb")
SCHEMA_ORG = StringIO.StringIO(file.read())
file.close()