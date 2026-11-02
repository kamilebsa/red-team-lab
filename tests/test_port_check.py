import unittest
from unittest.mock import patch

from src.recon.port_check import check_ports, identify_http, identify_service


class TestPortCheck(unittest.TestCase):

    def test_rejects_external_target(self):
        with self.assertRaises(ValueError):
            check_ports("8.8.8.8", [53])

    def test_rejects_ipv6_loopback(self):
        with self.assertRaises(ValueError):
            check_ports("::1", [80])

    def test_rejects_invalid_port_zero(self):
        with self.assertRaises(ValueError):
            check_ports("127.0.0.1", [0])

    def test_rejects_invalid_port_above_range(self):
        with self.assertRaises(ValueError):
            check_ports("127.0.0.1", [65536])

    def test_identifies_common_service(self):
        self.assertEqual(identify_service(22), "SSH")
        self.assertEqual(identify_service(443), "HTTPS")
        self.assertEqual(identify_service(9999), "Desconhecido")

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

        self.assertEqual(report["results"][0]["status"], "closed_or_filtered")

    def test_identifies_http_response(self):
        response = (
            b"HTTP/1.0 200 OK\r\n"
            b"Server: RedTeamLab-Test\r\n\r\n"
        )

        with patch("src.recon.port_check.socket.create_connection") as mock_connect:
            mock_connect.return_value.__enter__.return_value.recv.return_value = response
            result = identify_http("127.0.0.1", 45165)

        self.assertEqual(result["http_status"], "200")
        self.assertEqual(result["server"], "RedTeamLab-Test")
        self.assertIsNone(result["http_error"])

    def test_http_does_not_connect_to_external_target(self):
        with patch("src.recon.port_check.socket.create_connection") as mock_connect:
            result = identify_http("8.8.8.8", 80)

        mock_connect.assert_not_called()
        self.assertIsNone(result["http_status"])

    def test_http_rejects_unrecognized_response(self):
        with patch("src.recon.port_check.socket.create_connection") as mock_connect:
            mock_connect.return_value.__enter__.return_value.recv.return_value = (
                b"Resposta desconhecida\r\n"
            )
            result = identify_http("127.0.0.1", 45165)

        self.assertIsNone(result["http_status"])
        self.assertEqual(
            result["http_error"],
            "Resposta HTTP não reconhecida",
        )


if __name__ == "__main__":
    unittest.main()
