#!/usr/bin/env python3
"""Verificação controlada de portas no loopback local."""

import argparse
import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from ipaddress import ip_address

REPORTS = Path(__file__).resolve().parents[2] / "reports"

SERVICE_HINTS = {
    21: "FTP",
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8000: "HTTP alternativo",
    8001: "HTTP alternativo",
    8080: "HTTP alternativo",
    8443: "HTTPS alternativo",
}


def identify_service(port: int) -> str:
    return SERVICE_HINTS.get(port, "Desconhecido")


def identify_http(target: str, port: int) -> dict:
    """Obtém informações HTTP básicas somente no loopback IPv4."""
    result = {
        "http_status": None,
        "server": None,
        "http_error": None,
    }

    if target != "127.0.0.1":
        return result

    request = (
        f"HEAD / HTTP/1.0\r\n"
        f"Host: {target}\r\n"
        f"Connection: close\r\n\r\n"
    ).encode("ascii")

    try:
        with socket.create_connection((target, port), timeout=1) as sock:
            sock.sendall(request)
            response = sock.recv(4096).decode("iso-8859-1", errors="replace")

        lines = response.splitlines()
        if lines:
            parts = lines[0].split()
            if len(parts) >= 2 and parts[0].startswith("HTTP/"):
                result["http_status"] = parts[1]

        for line in lines[1:]:
            if line.lower().startswith("server:"):
                result["server"] = line.split(":", 1)[1].strip()
                break

        if result["http_status"] is None:
            result["http_error"] = "Resposta HTTP não reconhecida"

    except (OSError, UnicodeError) as exc:
        result["http_error"] = type(exc).__name__

    return result


def check_ports(target: str, ports: list[int]) -> dict:
    address = ip_address(target)
    if not address.is_loopback or address.version != 4:
        raise ValueError(
            "Escopo permitido nesta versão: somente loopback IPv4."
        )

    results = []
    for port in ports:
        if not 1 <= port <= 65535:
            raise ValueError(f"Porta inválida: {port}")

        status = "closed_or_filtered"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                if sock.connect_ex((target, port)) == 0:
                    status = "open"
        except OSError:
            status = "error"

        item = {
            "port": port,
            "status": status,
            "service_hint": identify_service(port),
        }

        if status == "open":
            item.update(identify_http(target, port))

        results.append(item)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "scope": "loopback_only",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default="127.0.0.1")
    parser.add_argument(
        "--ports",
        default="22,80,443,8000,8001,8080",
        help="Lista de portas separadas por vírgula",
    )
    args = parser.parse_args()

    try:
        ports = [int(value.strip()) for value in args.ports.split(",")]
        if not ports or len(set(ports)) != len(ports):
            raise ValueError("Informe portas únicas e não vazias.")

        report = check_ports(args.target, ports)
        REPORTS.mkdir(parents=True, exist_ok=True)
        output = REPORTS / "port-check.json"
        output.write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2))
        print(f"\nRelatório salvo em: {output}")
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
