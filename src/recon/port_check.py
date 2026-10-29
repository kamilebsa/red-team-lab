#!/usr/bin/env python3
"""Verificação controlada de portas no loopback local."""

import argparse
import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from ipaddress import ip_address

REPORTS = Path(__file__).resolve().parents[2] / "reports"


def check_ports(target: str, ports: list[int]) -> dict:
    address = ip_address(target)
    if not address.is_loopback:
        raise ValueError("Escopo permitido nesta versão: somente loopback.")

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

        results.append({"port": port, "status": status})

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
