"""
YuvaAI - DNS and TCP Diagnostic

Measures:
1. DNS resolution time
2. IPv4 connection time
3. IPv6 connection time
"""

import socket
import time


HOST = "api.groq.com"
PORT = 443
TIMEOUT = 5


def diagnose_network():

    print("\n========== YUVAAI NETWORK DIAGNOSTIC ==========")

    # --------------------------------------
    # 1. DNS RESOLUTION
    # --------------------------------------

    print("\n[1] DNS Resolution")

    start = time.perf_counter()

    try:

        addresses = socket.getaddrinfo(
            HOST,
            PORT,
            type=socket.SOCK_STREAM
        )

    except socket.gaierror as error:

        print("DNS failed:", error)
        return

    dns_time = time.perf_counter() - start

    print(f"DNS time: {dns_time:.4f}s")

    # --------------------------------------
    # 2. GET UNIQUE ADDRESSES
    # --------------------------------------

    unique_addresses = {}

    for family, socktype, protocol, canonname, sockaddr in addresses:

        key = (family, sockaddr)

        unique_addresses[key] = (
            family,
            socktype,
            protocol,
            sockaddr
        )

    print("\nResolved addresses:")

    for family, socktype, protocol, sockaddr in unique_addresses.values():

        version = (
            "IPv4" if family == socket.AF_INET else "IPv6"
        )

        print(f"{version}: {sockaddr[0]}")

    # --------------------------------------
    # 3. TEST TCP CONNECTIONS
    # --------------------------------------

    print("\n[2] TCP Connection Tests")

    family_counts = {
        socket.AF_INET: 0,
        socket.AF_INET6: 0
    }

    for family, socktype, protocol, sockaddr in unique_addresses.values():

        if family not in family_counts:
            continue

        if family_counts[family] >= 3:
            continue

        family_counts[family] += 1

        version = (
            "IPv4" if family == socket.AF_INET else "IPv6"
        )

        start = time.perf_counter()

        try:

            with socket.socket(
                family,
                socktype,
                protocol
            ) as connection:

                connection.settimeout(TIMEOUT)

                connection.connect(sockaddr)

            elapsed = time.perf_counter() - start

            print(
                f"{version} {sockaddr[0]}: "
                f"CONNECTED in {elapsed:.4f}s"
            )

        except OSError as error:

            elapsed = time.perf_counter() - start

            print(
                f"{version} {sockaddr[0]}: "
                f"FAILED after {elapsed:.4f}s - {error}"
            )

    print("\n========== DIAGNOSTIC COMPLETE ==========")


if __name__ == "__main__":

    diagnose_network()