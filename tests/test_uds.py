import unittest
from unittest.mock import MagicMock
from uds import UdsClient, SimpleServer
import threading
import time


class UdsClientTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        server_address = "/tmp/test_uds.sock"
        self.uds_client = UdsClient(server_address)
        self.simple_server = SimpleServer(server_address)

    def setUp(self):
        self.server_thread = threading.Thread(target=self.simple_server.run)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.1)  # Wait for simple_server to setup

    def test_get_key_not_exist(self):
        dpid = 1
        mac_address = "12:34:56:78:90:AB"

        # Get the value, whose key does not exist
        retrieved_val = self.uds_client.get(dpid, mac_address)

        # Check if the retrieved value matches the set value
        self.assertEqual(None, retrieved_val, "The retrieved value is not None")

    def test_contains_key(self):
        dpid = 1
        mac_address = "12:34:56:78:90:AB"
        val = 42

        # Contains the value
        is_contains = self.uds_client.contains(dpid, mac_address)

        # Check if the retrieved value matches the set value
        self.assertEqual(
            False, is_contains, "Key does not exist but contains returns True"
        )

        # Set the value
        self.uds_client.set(dpid, mac_address, val)

        # Contains the value
        is_contains = self.uds_client.contains(dpid, mac_address)

        # Check if the retrieved value matches the set value
        self.assertEqual(True, is_contains, "Key exists but contains returns False")

    def test_get_set_valid_mac_address(self):
        dpid = 1
        mac_address = "12:34:56:78:90:AB"
        val = 42

        # Set the value
        self.uds_client.set(dpid, mac_address, val)

        # Get the value
        retrieved_val = self.uds_client.get(dpid, mac_address)

        # Check if the retrieved value matches the set value
        self.assertEqual(
            val, retrieved_val, "The set and retrieved values do not match"
        )

    def test_invalid_mac_address(self):
        dpid = 1
        mac_address = "00:11:22:33:44:5Z"

        with self.assertRaises(ValueError):
            self.uds_client.get(dpid, mac_address)

        with self.assertRaises(ValueError):
            self.uds_client.set(dpid, mac_address, 5)


if __name__ == "__main__":
    unittest.main()
