import socket
import struct
import sys

import pyping
import encryptor

class PingTunnel(pyping.Ping):
    def __init__(self, destination: str, timeout: int, datafield: bytes, *args, **kwargs):
        self.datafield = datafield
        super().__init__(destination=destination, timeout=timeout, *args, **kwargs)
        self.response.packet_size = len(self.datafield)
    
    def send_one_ping(self, current_socket: socket.socket):
        """
        Send one ICMP ECHO_REQUEST
        """
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        checksum = 0

        # Make a dummy header with a 0 checksum.
        header = struct.pack(
            "!BBHHH", pyping.ICMP_ECHO, 0, checksum, self.own_id, self.seq_number
        )

        # padBytes = []
        # startVal = 0x42
        # for i in range(startVal, startVal + (self.packet_size)):
        #     padBytes += [(i & 0xff)]  # Keep chars in the 0-255 range
        # data = bytes(padBytes)
        data = self.datafield

        # Calculate the checksum on the data and the dummy header.
        checksum = pyping.calculate_checksum(header + data) # Checksum is in network order

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        header = struct.pack(
            "!BBHHH", pyping.ICMP_ECHO, 0, checksum, self.own_id, self.seq_number
        )

        packet = header + data

        send_time = pyping.default_timer()

        try:
            current_socket.sendto(packet, (self.destination, 1)) # Port number is irrelevant for ICMP
        except socket.error as e:
            self.response.output.append("General failure (%s)" % (e.args[1]))
            current_socket.close()
            return

        return send_time


def icmp_tunnel(hostname: str, data: bytes, filename='', timeout=1000, count=3, packet_size=1000, encrypt=False, *args, **kwargs):
    """
    send text to hostname using ICMP tunneling

    Args:
        hostname (str): hostname or ip address
        data (bytes): binary data what you want to send
        filename (str, optional): filename of `data`. Defaults to ''.
        timeout (int, optional):  Defaults to 1000.
        count (int, optional): how many reputations you send same packet. Defaults to 3.
        packet_size (int, optional): size of data field (in packet) at one time. Defaults to 1000.
        encrypt (bool, optional): data encryption with AES-CBC. Defaults to False.
    """
    
    metadata = f'{filename}\x1f{00000000:08}\x1f{len(data)}\x1f'.encode('utf-8')
    # data field structure == filename:id:content length:binary data (?????? ??? \x1f??? ???????????? ????????? ??????)
    # len(data)??? ?????? ????????? ??????, ????????? ????????? ????????? ??????
    # \x1f??? unit separator, ??????????????? ????????????????????? ???????????? ??????
    
    # `packet_size` ?????? ????????? ????????? (????????? 1000?????????)
    for i in range(0, len(data), packet_size - len(metadata)):
        
        metadata = f'{filename}\x1f{i//(packet_size - len(metadata)):08}\x1f{len(data)}\x1f'.encode('utf-8')
        splited_data = data[i:i + packet_size - len(metadata)]
        
        if encrypt:
            # ????????? ???????????? ????????? `packet_size`?????? ?????? ?????????
            datafield = encryptor.encrypt(metadata+splited_data)
        else:
            datafield = metadata + splited_data
        
        p = PingTunnel(hostname, timeout, datafield, *args, **kwargs)
        r = p.run(count)
        
        if r.ret_code == 0:
            print(f'[+] Ping {r.packet_size} bytes to {r.destination} and received pong')
        else:
            print(f'[-] Ping Failed {r.packet_size} bytes to {r.destination} (errno: {r.ret_code})')


if __name__ == '__main__':
    
    # arguments
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} <hostname> <filename> [-e]')
        exit(1)
    
    _, hostname, filename = sys.argv[:3]
    is_encrypt = True if len(sys.argv) == 4 and sys.argv[3] == '-e' else False
    print(f'send {filename} to {hostname} with {"encryption" if is_encrypt else "no encryption"}')
    
    # read file
    with open(filename, 'rb') as f:
        data = f.read()
        print(f'[+] Read {len(data)} bytes from {filename}')

    # run
    print('[+] sending..')
    icmp_tunnel(hostname=hostname, data=data, filename=filename, count=1, encrypt=is_encrypt)
    print('[+] done')
