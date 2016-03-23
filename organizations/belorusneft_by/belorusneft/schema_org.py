import StringIO

file = open("belorusneft/schema_org.xml", "rb")
SCHEMA_ORG = StringIO.StringIO(file.read())
file.close()