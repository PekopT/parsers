import StringIO

file = open("sgroshi/schema_org.xml", "rb")
SCHEMA_ORG = StringIO.StringIO(file.read())
file.close()