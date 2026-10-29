import unittest
from unittest.mock import patch

from src.recon.port_check import check_ports


class TestPortCheck(unittest.TestCase):

    def test_rejects_external_target(self):
        with self.assertRaises(ValueError):
            check_ports("8.8.8.8", [53])

    def test_rejects_invalid_port_zero(self):
        with self.assertRaises(ValueError):
            check_ports("127.0.0.1", [0])

    def test_rejects_invalid_port_above_range(self):
        with self.assertRaises(ValueError):
            check_ports("127.0.0.1", [65536])

    def test_detects_open_port(self):
        with patch("src.recon.port_check.socket.socket") as mock_socket:
            mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 0

            report = check_ports("127.0.0.1", [8000])

        self.assertEqual(report["scope"], "loopback_only")
        self.assertEqual(report["results"][0]["status"], "open")
        self.assertEqual(report["results"][0]["port"], 8000)

    def test_detects_closed_port(self):
        with patch("src.recon.port_check.socket.socket") as mock_socket:
            mock_socket.return_value.__enter__.return_value.connect_ex.return_value = 1

            report = check_ports("127.0.0.1", [9000])

        self.assertEqual(
            report["results"][0]["status"],
            "closed_or_filtered",
        )


if __name__ == "__main__":
    unittest.main()
