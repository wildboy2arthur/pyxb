SCHEMA_DIR=pyxb/standard/schemas
rm -rf pyxb/standard/bindings/raw
mkdir -p pyxb/standard/bindings/raw
touch pyxb/standard/bindings/raw/__init__.py
mkdir -p ${SCHEMA_DIR}

# Get a couple that we don't actually generate bindings for
test -f ${SCHEMA_DIR}/xml.xsd || wget -O ${SCHEMA_DIR}/xml.xsd http://www.w3.org/2001/xml.xsd
test -f ${SCHEMA_DIR}/XMLSchema.xsd || wget -O ${SCHEMA_DIR}/XMLSchema.xsd http://www.w3.org/2001/XMLSchema.xsd

( cat <<EOList
# NOTE: Use prefix xml_ instead of xml because xml conflicts with standard package
# This isn't really necessary, and currently fails resolution, so drop it
#http://www.w3.org/2001/xml.xsd xml_
# NOTE: XSD depends on XML which depends on XSD.  Since we have a workable
# XSD schema built-in, do not create an external pre-loaded schema for
# which we'll have to resolve in XML and subsequently in XSD.
#http://www.w3.org/2001/XMLSchema.xsd xsd
http://www.w3.org/2001/XMLSchema-hasFacetAndProperty xsd_hfp
http://schemas.xmlsoap.org/wsdl/ wsdl
http://www.w3.org/1999/xhtml.xsd xhtml
http://schemas.xmlsoap.org/soap/envelope/ soapenv
http://schemas.xmlsoap.org/soap/encoding/ soapenc
http://schemas.xmlsoap.org/wsdl/mime/ mime
http://schemas.xmlsoap.org/wsdl/soap/ soap
http://schemas.xmlsoap.org/wsdl/http/ http
http://schemas.xmlsoap.org/wsdl/soap12/wsdl11soap12.xsd soap12
#http://code.google.com/apis/kml/schema/kml21.xsd kml
http://www.w3.org/TR/2002/REC-xmldsig-core-20020212/xmldsig-core-schema.xsd xmldsig
http://www.w3.org/TR/2002/REC-xmlenc-core-20021210/xenc-schema.xsd xenc
http://docs.oasis-open.org/security/saml/v2.0/saml-schema-assertion-2.0.xsd saml_assert
http://docs.oasis-open.org/security/saml/v2.0/saml-schema-protocol-2.0.xsd saml_protocol
EOList
) | sed -e '/^#/d' \
  | while read uri prefix ; do
  cached_schema=${SCHEMA_DIR}/${prefix}.xsd
  if [ ! -f ${cached_schema} ] ; then
     echo "Retrieving ${prefix} from ${uri}"
     wget -O ${cached_schema} ${uri}
  fi
  scripts/pyxbgen \
    --module-path pyxb.standard.bindings.${prefix} \
    --schema-uri file:${cached_schema} \
    --generate-raw-binding \
    --save-component-model
done
