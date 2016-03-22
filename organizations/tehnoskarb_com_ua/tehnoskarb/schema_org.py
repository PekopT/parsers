import StringIO

file = open("tehnoskarb/schema_org.xml", "rb")
SCHEMA_ORG = StringIO.StringIO(file.read())
file.close()