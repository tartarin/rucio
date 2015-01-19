import requests
import os

SoapMessage = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:apachesoap="http://xml.apache.org/xml-soap" xmlns:impl="http://srm.lbl.gov/StorageResourceManager" xmlns:intf="http://srm.lbl.gov/StorageResourceManager" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/" xmlns:wsdlsoap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:tns="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >
<SOAP-ENV:Body>
<mns:srmPing xmlns:mns="http://srm.lbl.gov/StorageResourceManager" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<srmPingRequest xsi:type="impl:srmPingRequest">
<authorizationID soapenc:position="[0]" xsi:type="xsd:string">0</authorizationID>
</srmPingRequest></mns:srmPing></SOAP-ENV:Body></SOAP-ENV:Envelope>'''

import sys, httplib
import socket
import ssl
import os
import re
from httplib import HTTPSConnection
from urlparse import urlsplit

def get_proxy():
    """
    Return (host, port) if environment variable HTTPS_PROXY or
    https_proxy is found.  Otherwise return ().  Proxy variable value
    is assumed to be in the form of a URL like http://host[:port]/.
    If port is not given it defaults to 443.
    """
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if not proxy:
        return None
    proxy = urlsplit(proxy).netloc.split(":")
    if len(proxy) == 1:
        return (proxy, 443)
    return (proxy[0], int(proxy[1]))

def match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 rules
    are mostly followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    if not cert:
        raise ValueError("empty or no certificate")
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_to_pat(value).match(hostname):
                return
            dnsnames.append(value)
    if not dnsnames:
        # The subject is only checked when there is no DNSName entry
        # in subjectAltName
        for sub in cert.get('subject', ()):
            for key, value in sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                if key == 'commonName':
                    if _dnsname_to_pat(value).match(hostname):
                        return
                    dnsnames.append(value)
    if len(dnsnames) > 1:
        raise CertificateError("hostname %r "
            "doesn't match either of %s"
            % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError("hostname %r "
            "doesn't match %r"
            % (hostname, dnsnames[0]))
    else:
        raise CertificateError("no appropriate commonName or "
            "subjectAltName fields were found")

class VerifiedHTTPSConnection(HTTPSConnection):
    """
    Extension of Python's standard library HTTPSConnection which
    verifies the server certificate.
    """
    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 ca_certs=None):
        """
        Adds the ca_certs argument.

        @param ca_certs: File containing a concatination of x509
                         CA certificates that are trusted for verifying
                         the certificate of the remote server.
        """
        proxy = get_proxy()
        if proxy:
            real_host, real_port = host, port
            host, port = proxy

        HTTPSConnection.__init__(self, host, port, key_file, cert_file,
                                 strict, timeout)
        if proxy:
            if hasattr(self, "set_tunnel"):     # Python 2.7+
                self.set_tunnel(real_host, real_port)
            elif hasattr(self, "_set_tunnel"):  # Python 2.6.6 (private)
                self._set_tunnel(real_host, real_port)

        self.ca_certs = ca_certs

    def connect(self):
        """
        Identical to the standard library version except for the addition
        of the cert_reqs and ca_certs arguments to ssl.wrap_socket.
        """
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if hasattr(self, "_tunnel_host") and self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock,
                                    self.key_file,
                                    self.cert_file,
                                    server_side=False)

        match_hostname(self.sock.getpeercert(), self.host)


print SoapMessage

host = 'grid05.lal.in2p3.fr'
ca_certs_file = '/Users/garonne/Lab/rucio/tools/x509up'
port = 8446
path = '/srm/managerv2'

c = VerifiedHTTPSConnection(host=host, port=port, timeout=.5, key_file=ca_certs_file ,cert_file=ca_certs_file)
c.request("POST", path)
c.send(SoapMessage)
print dir(c.sock)
print c.sock.read()
#r = c.getresponse()

sys.exit(-1)
#construct and send the header

cert = '/Users/garonne/Lab/rucio/tools/x509up'
webservice = httplib.HTTPSConnection("grid05.lal.in2p3.fr", port=8446, key_file=cert, cert_file=cert)
webservice.putrequest("POST", "/srm/managerv2")
webservice.putheader("Host", "grid05.lal.in2p3.fr")
webservice.putheader("User-Agent", "Python post")
webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
webservice.putheader("Content-length", "%d" % len(SoapMessage))
webservice.putheader("SOAPAction", "\"\"")
webservice.endheaders()
webservice.send(SoapMessage)

# get the response

statuscode, statusmessage, header = webservice.getresponse()
print "Response: ", statuscode, statusmessage
print "headers: ", header
res = webservice.getfile().read()
print res

#url = 'https://grid05.lal.in2p3.fr:8446/srm/managerv2'
#headers = {'Content-type': "text/xml; charset=\"UTF-8\"",
#           'Content-length': "%d" % len(soapmsg),
#           }

#r = requests.post(url, cert='/Users/garonne/Lab/rucio/tools/x509up',
#                  verify=False, data=soapmsg, headers=headers,
#                  allow_redirects=False)


##r = post(url, headers=hds, data=data, verify=self.ca_cert, timeout=self.timeout)

#session = requests.Session()
#session.cert=os.getenv('X509_USER_PROXY')
#session.allow_redirects=True
#session.verify=False
#webservice.putrequest("POST", "/rcx-ws/rcx")
#webservice.putheader("Host", "www.pascalbotte.be")
#webservice.putheader("User-Agent", "Python post")
#webservice.putheader("SOAPAction", "\"\"")
#result = session.request('POST', url, data=soapmsg)
##
