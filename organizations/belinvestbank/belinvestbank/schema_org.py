import StringIO

file = open("belinvestbank/schema_org.xml", "rb")
SCHEMA_ORG = StringIO.StringIO(file.read())
file.close()