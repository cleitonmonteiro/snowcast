# -*- coding: utf-8 -*-

__author__ = 'Cleiton Monteiro'

"""
Universidade Federal do Ceará - Campus Russas 
Radio mp3   - Implementação de uma estação de radio simples via internet.
Projeto  01 - Redes de Computadores - 2018.2 - Prof. Filipe Maciel
"""

from snowcast.snowcast import ConexaoServidor
from sys import argv
from time import sleep
import socket

# $ snowcast_control <servidor> <porta servidor> <porta udp>
if len(argv) != 4:
  print("[ ? ] use : %s <ip_servidor> <porta_servidor> <porta_cliente_udp>" %(argv[0]))
  exit(-1)

enderecoServidor = (argv[1], int(argv[2]))
portaUdp         = int(argv[3])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.connect(enderecoServidor)
print("[<=>] Conectado com", enderecoServidor )

conexaoServidor = ConexaoServidor(sock, portaUdp , enderecoServidor)
print("[...] Gerenciando conexão com o servidor  ", enderecoServidor)
conexaoServidor.start()

sleep(.2)

promptOpcoes = 'Prompt Opções \n%10s : Encerrar \n%10s : SetStation \
               \n%10s : Listar os comandos do prompt' %('q','<Número>','help')

print(promptOpcoes)

while True:
  print("Prompt> ", end='')
  entrada = input()

  if entrada in ['q', 'Q']: # upper
    conexaoServidor.encerrarConecao()
    print('<Quit')  
    break

  if entrada in ['-h', '--h', 'help']:
    print(promptOpcoes)
    continue

  try:
    numStation = int(entrada)-1
    conexaoServidor.enviarSetEstation(numStation)
    print("[==>] setStation enviado para ", enderecoServidor, ' com número de estação ', numStation)
  except ValueError:
    print("[ ? ] erro: o valor dado não é um inteiro")
