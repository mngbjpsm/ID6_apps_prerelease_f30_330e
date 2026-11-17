import argparse
import socket
import struct
import threading
import unittest

from probe_signals import ecu_address, exchange, read_request


def frame(control, data):
    return struct.pack(">IH", len(data), control) + data


class ProbeTest(unittest.TestCase):
    def test_reply_filters_and_heartbeat(self):
        client, gateway = socket.socketpair()
        with client, gateway:
            gateway.settimeout(2)
            def respond():
                self.assertEqual(gateway.recv(11), frame(1, bytes.fromhex("f412224300")))
                gateway.sendall(frame(0x12, b""))
                self.assertEqual(gateway.recv(8), frame(0x13, bytes.fromhex("00f4")))
                for value in ("18f46243000000", "12f47f2278", "12f46243000bf8"):
                    gateway.sendall(frame(1, bytes.fromhex(value)))
            thread = threading.Thread(target=respond)
            thread.start()
            result = exchange(client, 0x12, read_request("224300"))
            thread.join(3)
            self.assertFalse(thread.is_alive())
            self.assertEqual(result, {"reply": "62 43 00 0b f8", "data": "0b f8"})

    def test_refuses_actuation_and_decodes_negative_reply(self):
        for text in ("2f0100", "2e430001", "14ffffff", "2243", "01050c"):
            with self.assertRaises(argparse.ArgumentTypeError):
                read_request(text)
        client, gateway = socket.socketpair()
        with client, gateway:
            gateway.sendall(frame(1, bytes.fromhex("12f47f2231")))
            self.assertEqual(exchange(client, 0x12, read_request("22586f"))["nrc"], "31")

    def test_hybrid_ecus_and_multi_value_reply(self):
        self.assertEqual([ecu_address(text) for text in ("07", "12", "18", "1A", "1a", "3A")],
                         ["07", "12", "18", "1a", "1a", "3a"])
        for text in ("7", "00", "40", "f4", "df", "012"):
            with self.assertRaises(argparse.ArgumentTypeError):
                ecu_address(text)
        client, gateway = socket.socketpair()
        with client, gateway:
            # A DME reply to the same request must not be taken for the SME's.
            for value in ("12f462ddbc0000", "07f462ddbc02a303b60046"):
                gateway.sendall(frame(1, bytes.fromhex(value)))
            result = exchange(client, int(ecu_address("07"), 16), read_request("22ddbc"))
            self.assertEqual(gateway.recv(11), frame(1, bytes.fromhex("f40722ddbc")))
            self.assertEqual(result["data"], "02 a3 03 b6 00 46")


if __name__ == "__main__":
    unittest.main()
