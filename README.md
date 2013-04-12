unicode_xml_parser
==================

Subclasses the the TreeBuilder to make it more Unicode friendly. Closer adherence to the XML spec.

At the moment the attributes now support full unicode but the CDATA still
only supports 0-256 for some reason. Still more work to be done. This is
helpful in cases like when we are using IronPython and don't have access to
lxml and don't want to or can't use the C# xml libraries.