#!/usr/bin/env python3
"""
gen.py — Generador de captura PCAP con credenciales FTP  [SOLO DOCENTE]
========================================================================
Genera captura.pcap: tráfico FTP con la flag como contraseña.
Requiere scapy: pip install scapy

USO:
    sudo python3 gen.py          (necesita root para crear raw packets)
    # ó
    python3 gen.py               (scapy puede funcionar sin root en algunos sistemas)
"""
FLAG = "CTF{sniffing_texto_plano_es_peligroso}"

try:
    from scapy.all import (
        IP, TCP, Ether, Raw, wrpcap, RandShort,
        Packet, bind_layers, StreamSocket
    )
    SCAPY = True
except ImportError:
    SCAPY = False


def build_pcap_manual():
    """
    Construye un PCAP mínimo manualmente (formato pcap clásico).
    No requiere scapy. Incluye paquetes TCP simulados con texto FTP.
    """
    import struct, socket, time

    def pcap_global_header():
        # Magic, version_major, version_minor, thiszone, sigfigs, snaplen, network
        return struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)

    def pcap_packet(data: bytes, ts_sec: int, ts_usec: int) -> bytes:
        return struct.pack("<IIII", ts_sec, ts_usec, len(data), len(data)) + data

    def ethernet_ip_tcp(src_ip, dst_ip, sport, dport, seq, ack, flags, payload):
        """Construye un frame Ethernet/IP/TCP mínimo."""
        # Ethernet header (14 bytes): dst_mac, src_mac, ethertype
        eth = (b"\x00\x50\x56\xc0\x00\x01"   # dst MAC (servidor)
               b"\x00\x0c\x29\xab\xcd\xef"   # src MAC (cliente)
               b"\x08\x00")                   # EtherType: IPv4

        payload_bytes = payload.encode() if isinstance(payload, str) else payload
        tcp_len = 20 + len(payload_bytes)
        ip_len = 20 + tcp_len

        # IP header (20 bytes, sin opciones)
        ip = struct.pack(">BBHHHBBH4s4s",
            0x45,                                   # version+IHL
            0,                                      # DSCP
            ip_len,                                 # total length
            0x1234,                                 # ID
            0x4000,                                 # flags+fragment
            64,                                     # TTL
            6,                                      # protocol TCP
            0,                                      # checksum (0 = ignorar)
            socket.inet_aton(src_ip),
            socket.inet_aton(dst_ip),
        )

        # TCP header (20 bytes, sin opciones)
        # flags: SYN=0x02 ACK=0x10 PSH=0x08 FIN=0x01
        tcp = struct.pack(">HHIIBBHHH",
            sport, dport,
            seq, ack,
            0x50,    # data offset (5 words = 20 bytes)
            flags,
            65535,   # window
            0,       # checksum (0 = ignorar)
            0,       # urgent
        ) + payload_bytes

        return eth + ip + tcp

    CLIENT = "192.168.1.50"
    SERVER = "192.168.1.1"
    SPORT  = 54321
    DPORT  = 21    # FTP control

    ts = int(time.time()) - 300

    # Conversación FTP simulada
    frames = [
        # SYN (cliente → servidor)
        (CLIENT, SERVER, SPORT, DPORT, 1000, 0, 0x02, b""),
        # SYN-ACK (servidor → cliente)
        (SERVER, CLIENT, DPORT, SPORT, 5000, 1001, 0x12, b""),
        # ACK
        (CLIENT, SERVER, SPORT, DPORT, 1001, 5001, 0x10, b""),
        # Banner FTP del servidor
        (SERVER, CLIENT, DPORT, SPORT, 5001, 1001, 0x18,
         b"220 CorpFTP Server v2.1 - Bienvenido\r\n"),
        # USER comando
        (CLIENT, SERVER, SPORT, DPORT, 1001, 5040, 0x18,
         b"USER administrador\r\n"),
        # 331 Password required
        (SERVER, CLIENT, DPORT, SPORT, 5040, 1021, 0x18,
         b"331 Password required for administrador\r\n"),
        # PASS con la flag como contraseña
        (CLIENT, SERVER, SPORT, DPORT, 1021, 5081, 0x18,
         f"PASS {FLAG}\r\n".encode()),
        # 230 Login successful
        (SERVER, CLIENT, DPORT, SPORT, 5081, 1061, 0x18,
         b"230 Login successful.\r\n"),
        # Tráfico de ruido (HTTP a otro servidor)
        (CLIENT, "8.8.8.8", 44444, 80, 2000, 0, 0x18,
         b"GET / HTTP/1.1\r\nHost: ejemplo.com\r\n\r\n"),
        ("8.8.8.8", CLIENT, 80, 44444, 9000, 2040, 0x18,
         b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nHello"),
        # QUIT FTP
        (CLIENT, SERVER, SPORT, DPORT, 1061, 5103, 0x18,
         b"QUIT\r\n"),
        (SERVER, CLIENT, DPORT, SPORT, 5103, 1067, 0x18,
         b"221 Goodbye.\r\n"),
    ]

    packets = []
    for i, (src, dst, sp, dp, seq, ack, flags, payload) in enumerate(frames):
        frame = ethernet_ip_tcp(src, dst, sp, dp, seq, ack, flags, payload)
        packets.append(pcap_packet(frame, ts + i, i * 100000))

    with open("captura.pcap", "wb") as f:
        f.write(pcap_global_header())
        for pkt in packets:
            f.write(pkt)

    print("[+] captura.pcap generada (modo manual, sin scapy)")
    print(f"[+] La flag '{FLAG}' está en el comando PASS del flujo FTP")


def build_pcap_scapy():
    """Genera captura.pcap usando scapy (más fiel a Wireshark)."""
    from scapy.all import IP, TCP, Ether, Raw, wrpcap

    CLIENT = "192.168.1.50"
    SERVER = "192.168.1.1"
    SPORT  = 54321
    DPORT  = 21

    def pkt(src, dst, sp, dp, flags, payload=b"", seq=0, ack=0):
        return (
            Ether(src="00:0c:29:ab:cd:ef", dst="00:50:56:c0:00:01")
            / IP(src=src, dst=dst)
            / TCP(sport=sp, dport=dp, flags=flags, seq=seq, ack=ack)
            / Raw(load=payload)
        )

    pkts = [
        pkt(SERVER, CLIENT, DPORT, SPORT, "PA", b"220 CorpFTP Server v2.1\r\n", 5000, 1001),
        pkt(CLIENT, SERVER, SPORT, DPORT, "PA", b"USER administrador\r\n", 1001, 5025),
        pkt(SERVER, CLIENT, DPORT, SPORT, "PA", b"331 Password required\r\n", 5025, 1021),
        pkt(CLIENT, SERVER, SPORT, DPORT, "PA", f"PASS {FLAG}\r\n".encode(), 1021, 5048),
        pkt(SERVER, CLIENT, DPORT, SPORT, "PA", b"230 Login successful.\r\n", 5048, 1070),
        # Tráfico de ruido HTTP
        pkt(CLIENT, "8.8.8.8", 44444, 80, "PA",
            b"GET / HTTP/1.1\r\nHost: ejemplo.com\r\n\r\n", 2000, 0),
        pkt("8.8.8.8", CLIENT, 80, 44444, "PA",
            b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK", 9000, 2052),
        pkt(CLIENT, SERVER, SPORT, DPORT, "PA", b"QUIT\r\n", 1070, 5070),
        pkt(SERVER, CLIENT, DPORT, SPORT, "PA", b"221 Goodbye.\r\n", 5070, 1076),
    ]

    wrpcap("captura.pcap", pkts)
    print("[+] captura.pcap generada con scapy")
    print(f"[+] La flag '{FLAG}' está en el paquete FTP PASS")


if __name__ == "__main__":
    if SCAPY:
        build_pcap_scapy()
    else:
        print("[!] Scapy no disponible. Usando generador manual...")
        build_pcap_manual()
