# -*- coding: utf-8 -*-

__author__ = 'Cleiton Monteiro'

"""
Universidade Federal do Ceará - Campus Russas 
Radio mp3   - Implementação de uma estação de radio simples via internet.
Projeto  01 - Redes de Computadores - 2018.2 - Prof. Filipe Maciel
"""

from sys import argv
import socket

if len(argv) != 2:
  print("[ ? ] use : %s <porta_udp>" %(argv[0]))
  exit(-1)

portaUDP = int(argv[1])
# ip = socket.gethostbyname(socket.gethostname())
# ip = '192.168.1.12'
ip = '127.0.0.1'
endereco = (ip, portaUDP)
sock     = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


sock.bind(endereco)

# 16KiB/s
READING_SIZE = 16384
while True:
  try:
    dados, endereco_conexao = sock.recvfrom(READING_SIZE)
    print(dados)
  except:
    pass

sock.close()