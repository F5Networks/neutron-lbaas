# Copyright 2015-2016 Hewlett-Packard Development Company, L.P.
# Copyright 2016 Rackspace Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from OpenSSL import crypto
from oslo_log import log as logging
import six
from tempest import config

config = config.CONF

LOG = logging.getLogger(__name__)


class BarbicanTestHelper(object):

    def __init__(self, barbican_client):
        self.barbican_client = barbican_client

    def _create_certificate_chain(self):
        """
        Construct and return a chain of certificates.

            1. A new self-signed certificate authority certificate (cacert)
            2. A new intermediate certificate signed by cacert (icert)
            3. A new server certificate signed by icert (scert)
            4. Returns server certificate and server key (s_cert, s_key)
        """
        caext = crypto.X509Extension('basicConstraints', False, 'CA:true')

        # Step 1
        cakey = crypto.PKey()
        cakey.generate_key(crypto.TYPE_RSA, 1024)
        cacert = crypto.X509()
        cacert.get_subject().CN = "Authority Certificate"
        cacert.set_issuer(cacert.get_subject())
        cacert.set_pubkey(cakey)
        cacert.gmtime_adj_notBefore(0)
        cacert.gmtime_adj_notAfter(315360000)
        cacert.set_serial_number(1)
        cacert.sign(cakey, "sha1")
        self.ca_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cacert)
        self.ca_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, cakey)

        # Step 2
        ikey = crypto.PKey()
        ikey.generate_key(crypto.TYPE_RSA, 1024)
        icert = crypto.X509()
        icert.get_subject().CN = "ca-int@acme.com"
        icert.set_issuer(icert.get_subject())
        icert.set_pubkey(ikey)
        icert.gmtime_adj_notBefore(0)
        # 315360000 can be substituted with 10*365*24*60*60
        icert.gmtime_adj_notAfter(315360000)
        icert.add_extensions([caext])
        icert.set_serial_number(1)
        icert.sign(cakey, "sha1")
        self.i_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cacert)
        self.i_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, cakey)

        # Step 3
        skey = crypto.PKey()
        skey.generate_key(crypto.TYPE_RSA, 1024)
        scert = crypto.X509()
        scert.get_subject().CN = "server@acme.com"
        scert.set_issuer(scert.get_subject())
        scert.set_pubkey(skey)
        scert.gmtime_adj_notBefore(0)
        scert.gmtime_adj_notAfter(315360000)
        scert.add_extensions([
            crypto.X509Extension('basicConstraints', True, 'CA:false')])
        scert.set_serial_number(1)
        scert.sign(ikey, "sha1")
        self.s_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, icert)
        self.s_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, ikey)

        return [(self.s_key, self.s_cert)]

    def _create_container_and_secrets(self):
        cert = self.barbican_client.secrets.create(
            name='server_cert',
            algorithm='aes',
            bit_length=256,
            mode='cbc',
            payload=self.s_cert,
            payload_content_type='text/plain'
        )
        cert_store = cert.store()
        cert_secret = self.barbican_client.secrets.get(cert_store)

        pk = self.barbican_client.secrets.create(
            name='server_key',
            algorithm='aes',
            bit_length=256,
            mode='cbc',
            payload=self.s_key,
            payload_content_type='text/plain'
        )
        pk_store = pk.store()
        pk_secret = self.barbican_client.secrets.get(pk_store)

        container = (
            self.barbican_client.containers.create_certificate(
                name='tls-lb-container',
                certificate=cert_secret,
                private_key=pk_secret
            )
        )
        tls_container_ref = container.store()
        return tls_container_ref

    def create_barbican_resources(self):
        self._create_certificate_chain()
        return self._create_container_and_secrets()

    def cleanup_barbican(self, tls_container_id):
        certificate_container = self.barbican_client.containers.get(
            tls_container_id)
        for type, ref in six.iteritems(certificate_container.secret_refs):
            self.barbican_client.secrets.delete(secret_ref=ref)
        certificate_container.delete()

