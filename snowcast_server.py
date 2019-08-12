# -*- coding: utf-8 -*-

__author__ = 'Cleiton Monteiro'

"""
Universidade Federal do Ceará - Campus Russas 
Radio mp3   - Implementação de uma estação de radio simples via internet.
Projeto  01 - Redes de Computadores - 2018.2 - Prof. Filipe Maciel
"""

from snowcast.snowcast import criarThreadsEstacoes
from snowcast.snowcast import ControleAccept
from snowcast.snowcast import READING_SIZE
from sys import argv, stdin

from time import sleep

# $ snowcast_server <porta tcp> <arquivo1> . . .
if len(argv) < 3:
  print("[ ? ] Use : %s <porta_tcp> <arquivo_1> ... <arquivo_n>" %(argv[0]))
  exit(-1)

portaTCP = int(argv[1])
backlog  = 10
estacoes = criarThreadsEstacoes(argv[2:], READING_SIZE) 
controleClientes = []

# ip = socket.gethostbyname(socket.gethostname())

ip = '127.0.0.1'

# ip = '192.168.1.12'
controleAccept = ControleAccept(ip, portaTCP, backlog, estacoes, controleClientes)
controleAccept.start()

sleep(.2)

promptOpcoes = 'Prompt Opções \n%6s : Encerrar \n%6s : Listar os clientes por estação\
              \n%6s : Listar os comandos do prompt' %('q', 'p', 'help')

print(promptOpcoes)
while True:
  print("Prompt> ", end='')
  
  entrada = input()
  
  if entrada in ['Q', 'q']:
    controleAccept.encerrar()
    for estacao in estacoes:
      if estacao.sock:
        estacao.encerrar()
    print("[...] Encerrando os controles dos clientes...")
    for cc in controleClientes:
      print("[...] Controle cliente ", cc.addrCliente, " encerrado.")
      cc.encerrar()
    print("<Quit")
    break

  if entrada in ['P', 'p']:
    for i, estacao in enumerate(estacoes):
      print("Estação %3i [ %40s ] " %(i, estacao.nomeMusica), end='')
      if not len(estacao.clientes) or not estacao.status:
        print('{Estação vazia}')
      else:
        print()
        for c in estacao.clientes:
          print('\tCliente ', c.endereco)
        print()        

  elif entrada in ['-h', '--h', 'help']:
    print(promptOpcoes)
