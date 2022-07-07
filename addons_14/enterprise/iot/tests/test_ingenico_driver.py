from unittest.mock import MagicMock, patch
from zlib import crc32

from odoo.tests.common import BaseCase


class TestOutgoingIngenicoMessage(BaseCase):
    @patch.dict(
        "sys.modules", {
            # Mock out all of hw_drivers to avoid side-effects from starting services,
            # additional dependencies and modifying global imports
            "odoo.addons.hw_drivers": MagicMock(),
            # Mock the modules IngenicoDriver imports so the imports don't fail
            "odoo.addons.hw_drivers.driver": MagicMock(),
            "odoo.addons.hw_drivers.event_manager": MagicMock(),
            "odoo.addons.hw_drivers.iot_handlers.interfaces.SocketInterface": MagicMock(),
        }
    )
    def setUp(self):
        from odoo.addons.iot.iot_handlers.drivers.IngenicoDriver import OutgoingIngenicoMessage

        self.OutgoingIngenicoMessage = OutgoingIngenicoMessage
        self.dev = MagicMock()
        self.msg = self.OutgoingIngenicoMessage(
            dev=self.dev,
            terminalId=b"1",
            ecrId="1",
            protocolId=b"1",
            messageType="TransactionRequest",
            sequence=b"1",
            transactionId=1,
            amount=1,
        )

    def test_mdc_tag_length(self):
        # 1 byte for the tag + 1 byte for the length + 4 bytes for the CRC
        self.assertEqual(len(self.msg._generateMDC(b"dummy")), 6)

    def test_unpadded_crc(self):
        content = bytes(11)

        # An even length CRC, which doesn't require padding
        crc = '{:x}'.format(crc32(content))
        self.assertEqual(crc, '6b87b1ec')
        self.assertEqual(len('{:x}'.format(crc32(content))), 8)

        # Verify the CRC has the expected length and no errors are thrown
        self.assertEqual(len(self.msg._getCRC32(content)), 4)

    def test_padded_crc(self):
        content = bytes(13)

        # An odd length CRC, which does require padding
        crc = '{:x}'.format(crc32(content))
        self.assertEqual(crc, 'f744682')
        self.assertEqual(len('{:x}'.format(crc32(content))), 7)

        # Verify the CRC has the expected length and no errors are thrown
        self.assertEqual(len(self.msg._getCRC32(content)), 4)
