import StringIO

SCHEMA_ORG = StringIO.StringIO("""\
<?xml version="1.0" encoding="UTF-8"?>

<rng:grammar xmlns:rng="http://relaxng.org/ns/structure/1.0"

        ns=""

        datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes">



    <rng:start>

        <rng:ref name="company"/>

    </rng:start>



    <rng:define name="company">

        <rng:element name="company">

            <rng:interleave>

                <rng:element name="company-id">

                    <rng:data type="token"/>

                </rng:element>



                <rng:ref name="actualization-date"/>



                <rng:zeroOrMore>

                    <rng:element name="name">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="name-other">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:ref name="phone"/>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="email">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:optional>

                    <rng:element name="url">

                        <rng:ref name="uri"/>

                    </rng:element>

                </rng:optional>



                <rng:zeroOrMore>

                    <rng:element name="add-url">

                        <rng:ref name="uri"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:oneOrMore>

                    <rng:element name="rubric-id">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:oneOrMore>



                <rng:zeroOrMore>

                    <rng:element name="working-time">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="address">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="country">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:optional>

                    <rng:element name="post-index">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="house">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="house-add">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="corps">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="build">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="possession">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="km">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:zeroOrMore>

                    <rng:element name="admn-area">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="sub-admn-area">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="locality-name">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="sub-locality-name">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="street">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:element name="address-add">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:optional>

                    <rng:ref name="coordinates"/>

                </rng:optional>



                <rng:zeroOrMore>

                    <rng:element name="info-page">

                        <rng:ref name="uri"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:optional>

                    <rng:element name="description">

                        <rng:ref name="StringDataWithLangAttr"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:ref name="photos"/>

                </rng:optional>



                <rng:zeroOrMore>

                    <rng:element name="add-info">

                        <rng:data type="string"/>

                    </rng:element>

                </rng:zeroOrMore>



                <rng:zeroOrMore>

                    <rng:ref name="feature"/>

                </rng:zeroOrMore>

            </rng:interleave>

        </rng:element>

    </rng:define>



    <rng:define name="StringDataWithLangAttr">

        <rng:optional>

            <rng:attribute name="lang" a0:defaultValue="ru" xmlns:a0="http://relaxng.org/ns/compatibility/annotations/1.0">

                <rng:data type="string">

                    <rng:param name="pattern">[a-z][a-z]</rng:param>

                </rng:data>

            </rng:attribute>

        </rng:optional>

        <rng:data type="string"/>

    </rng:define>



    <rng:define name="uri">

        <rng:data type="string">

            <rng:param name="pattern">https?://((([\p{L}0-9_\-]+\.)+\p{L}{2,63})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})|localhost)(:[0-9]+)?(/.*)?</rng:param>

        </rng:data>

    </rng:define>



    <rng:define name="phone">

        <rng:element name="phone">

            <rng:interleave>

                <rng:optional>

                    <rng:element name="ext">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="type">

                        <rng:choice>

                            <rng:value>phone</rng:value>

                            <rng:value>fax</rng:value>

                            <rng:value>phone-fax</rng:value>

                        </rng:choice>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="number">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="info">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:optional>



            </rng:interleave>

        </rng:element>

    </rng:define>



    <rng:define name="coordinates">

        <rng:element name="coordinates">

            <rng:interleave>

                <rng:optional>

                    <rng:element name="lon">

                        <rng:data type="float"/>

                    </rng:element>

                </rng:optional>



                <rng:optional>

                    <rng:element name="lat">

                        <rng:data type="float"/>

                    </rng:element>

                </rng:optional>

            </rng:interleave>

        </rng:element>

    </rng:define>



    <rng:define name="photos">

        <rng:element name="photos">

            <rng:zeroOrMore>

                <rng:ref name="photo"/>

            </rng:zeroOrMore>



            <rng:attribute name="gallery-url">

                <rng:ref name="uri"/>

            </rng:attribute>

        </rng:element>

    </rng:define>



    <rng:define name="photo">

        <rng:element name="photo">

            <rng:attribute name="url">

                <rng:ref name="uri"/>

            </rng:attribute>



            <rng:optional>

                <rng:attribute name="alt">

                    <rng:data type="string"/>

                </rng:attribute>

            </rng:optional>



            <rng:optional>

                <rng:attribute name="type">

                    <rng:choice>

                        <rng:value>interior</rng:value>

                        <rng:value>exterior</rng:value>

                    </rng:choice>

                </rng:attribute>

            </rng:optional>

        </rng:element>

    </rng:define>



    <rng:define name="add-info">

        <rng:element name="add-info">

            <rng:oneOrMore>

                <rng:element name="param">

                    <rng:element name="name">

                        <rng:data type="token"/>

                    </rng:element>

                    <rng:element name="value">

                        <rng:data type="token"/>

                    </rng:element>

                </rng:element>

            </rng:oneOrMore>

        </rng:element>

    </rng:define>



    <rng:define name="actualization-date">

        <rng:element name="actualization-date">

            <rng:data type="string">

                <rng:param name="pattern">\d{13}|\d{10}|\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}</rng:param>

            </rng:data>

        </rng:element>

    </rng:define>



    <rng:define name="featureType">

        <rng:attribute name="name">

            <rng:data type="string"/>

        </rng:attribute>

    </rng:define>



    <rng:define name="featureBooleanType">

        <rng:attribute name="name">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:attribute name="value">

            <rng:choice>

                <rng:value>1</rng:value>

                <rng:value>0</rng:value>

            </rng:choice>

        </rng:attribute>

    </rng:define>



    <rng:define name="featureUnitableType">

        <rng:attribute name="name">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:attribute name="value">

            <rng:data type="decimal"/>

        </rng:attribute>



        <rng:attribute name="unit">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:attribute name="unit-value">

            <rng:data type="string"/>

        </rng:attribute>

    </rng:define>



    <rng:define name="featureEnumType">

        <rng:attribute name="name">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:attribute name="value">

            <rng:data type="string"/>

        </rng:attribute>

    </rng:define>



    <rng:define name="featureNumericType">

        <rng:attribute name="name">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:attribute name="value">

            <rng:data type="decimal"/>

        </rng:attribute>

    </rng:define>



    <rng:define name="featureRangeType">

        <rng:attribute name="name">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:optional>

            <rng:attribute name="from">

                <rng:data type="string"/>

            </rng:attribute>

        </rng:optional>



        <rng:optional>

            <rng:attribute name="to">

                <rng:data type="string"/>

            </rng:attribute>

        </rng:optional>

    </rng:define>



    <rng:define name="featureRangeUnitType">

        <rng:attribute name="name">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:optional>

            <rng:attribute name="from">

                <rng:data type="decimal"/>

            </rng:attribute>

        </rng:optional>



        <rng:optional>

            <rng:attribute name="to">

                <rng:data type="decimal"/>

            </rng:attribute>

        </rng:optional>



        <rng:attribute name="unit">

            <rng:data type="string"/>

        </rng:attribute>



        <rng:attribute name="unit-value">

            <rng:data type="string"/>

        </rng:attribute>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-boolean">

            <rng:ref name="featureBooleanType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-single">

            <rng:ref name="featureType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-multiple">

            <rng:ref name="featureType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-enum-single">

            <rng:ref name="featureEnumType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-enum-multiple">

            <rng:ref name="featureEnumType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-numeric-single">

            <rng:ref name="featureNumericType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-numeric-multiple">

            <rng:ref name="featureNumericType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-in-units-single">

            <rng:ref name="featureUnitableType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-in-units-multiple">

            <rng:ref name="featureUnitableType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-range-single">

            <rng:ref name="featureRangeType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-range-multiple">

            <rng:ref name="featureRangeType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-range-in-units-single">

            <rng:ref name="featureRangeUnitType"/>

        </rng:element>

    </rng:define>



    <rng:define name="feature" combine="choice">

        <rng:element name="feature-range-in-units-multiple">

            <rng:ref name="featureRangeUnitType"/>

        </rng:element>

    </rng:define>

</rng:grammar>
""")
