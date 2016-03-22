import StringIO

file = open("laguna/schema_org.xml", "rb")
SCHEMA_ORG = StringIO.StringIO(file.read())
file.close()