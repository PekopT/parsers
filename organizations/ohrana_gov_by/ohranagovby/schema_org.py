import StringIO

file = open("ohranagovby/schema_org.xml", "rb")
SCHEMA_ORG = StringIO.StringIO(file.read())
file.close()