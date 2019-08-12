# -*- coding: utf-8 -*-

__author__ = 'Cleiton Monteiro'

"""
Universidade Federal do Ceará - Campus Russas 
Radio mp3   - Implementação de uma estação de radio simples via internet.
Projeto  01 - Redes de Computadores - 2018.2 - Prof. Filipe Maciel
"""

from threading import Thread
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from sys import byteorder as sbyteorder
from ctypes import c_uint8 , c_uint16
from time import sleep

# 16KiB/s
READING_SIZE = 16384

class Comandos:
    """
    Protocolo: comandos para estabeler o protocolo entre o cliente e o servidor.
    Esses são números inteiro sem sinal de 8 bits cada um( ctypes.c_uint8 ).

    invalidCommand = 2\n
    setStation     = 1\n
    welcome        = 0\n
    announce       = 1\n
    hello          = 0
    """
    invalidCommand = 2
    setStation     = 1
    announce       = 1
    welcome        = 0
    hello          = 0

    def __init__(self):
        pass

class Cliente():
  """
  Modelagem de um cliente para a radio-mp3
  """
  def __init__(self, idCliente,endereco, sockTcp, portaUdp, numEstacao, controle):
    self.idCliente  = idCliente
    self.endereco   = endereco
    self.sockTcp    = sockTcp
    self.portaUdp   = portaUdp
    self.numEstacao = numEstacao
    self.controle   = controle

class Estacao(Thread):
  """
  Thread : gerencia uma estação, onde é feito o envio de uma música para os clientes que estão
  conectados a estação.
  """

  def __init__(self, idEstacao, arquivo, readingSize=4096):
    self.idEstacao    = idEstacao
    self.arquivo      = arquivo
    self.__clientes   = []
    self.status       = False
    self.readingSize  = readingSize
    self.sock         = None
    self.__bytesMusica= []
    self.nomeMusica   = arquivo[:-4]
    self.__bufferAdd  = []
    self.__bufferRm   = []
    self.__stop       = False
    Thread.__init__(self)

  def run(self):
    try:
      if not self.__prepararMusica():
        print("[ ? ] erro: na leitura do arquivo ( ", self.arquivo, " ) na estação ", self.idEstacao)
        print("Fechando estação ", self.idEstacao)
        self.status = False
        exit(0)

      self.sock = socket(AF_INET, SOCK_DGRAM)
      self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

      while not self.__stop:
        if self.status:
          for b in self.__bytesMusica:
            for cliente in self.__clientes:
              self.sock.sendto(b, (cliente.endereco[0], cliente.portaUdp))
            
            if self.__bufferAdd:
              self.__addCliente()

            if self.__bufferRm:
              self.__rmCliente()

            sleep(1)

          for c in self.__clientes:
            c.controle.enviarAnnounce(self.nomeMusica)

      self.sock.close()
    except:
      exit(0)

  def __prepararMusica(self):
    """
    Ler o arquivo da música em modo binário e criar um lista com os dados
    lidos com cada elemento com tamanho de readingSize.
    """
    # erro
    try:
      musica = open(self.arquivo, 'rb')
      dados = musica.read(self.readingSize)
      while dados:
        self.__bytesMusica.append(dados)
        dados = musica.read(self.readingSize)
      musica.close()
      return True
    except:
      return False

  def addCliente(self, cliente):
    self.__bufferAdd.append(cliente)

  def __addCliente(self):
    for cb in self.__bufferAdd:
      self.__clientes.append(cb)
    self.__bufferAdd = []

  def rmCliente(self, cliente):
    self.__bufferRm.append(cliente)

  def __rmCliente(self):
    for cb in self.__bufferRm:
      for c in self.__clientes:
        if c.idCliente == cb.idCliente:
          self.__clientes.remove(c)
    self.__bufferRm = []

  @property
  def clientes(self):
    while self.__bufferAdd or self.__bufferRm:
      pass
    return self.__clientes

  def encerrar(self):
    print("[...] Encerrando estação %3i [ %40s ] " %(self.idEstacao, self.nomeMusica))
    try:   
      self.sock.shutdown(0)
      self.sock.close()    
    except:
      self.__stop = True
    print("[XXX] Estação  ", self.idEstacao, ' encerrada.')

class ControleAccept(Thread):
  """
  Thread : espera por conexões dos clientes, aceita e depois passa a conexão para ControleCliente.
  self.estacoes --> Threads
  """

  def __init__(self, ip ,portaTcp, backlog, estacoes, controle):
    self.ip       = ip
    self.portaTcp = portaTcp
    self.backlog  = backlog
    self.estacoes = estacoes
    self.controle = controle
    self.sock     = None
    Thread.__init__(self)

  def run(self):
    try:
      self.sock = socket(AF_INET, SOCK_STREAM)
      self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)      
      
      self.sock.bind((self.ip, self.portaTcp))
      print("[...] %8s : addr (%s:%i )" % ("Bind", self.ip, self.portaTcp))
      self.sock.listen(self.backlog)
      print("[...] %8s : backlog (%i)" % ('Listen', self.backlog))

      idCliente = 0
      while True:
        print("[...] Aguardando conexões...")
        connSock, addrCliente = self.sock.accept()
        print("\n[<==] %8s : cliente " % ("Accept"), end='')
        print(addrCliente)

        print("[<=>] %8s : conexão estabelecida com" % ("Accept"), end='')
        print(addrCliente)

        print("[...] Gerenciando cliente ", addrCliente)

        cc = ControleCliente(idCliente, connSock, addrCliente, self.estacoes)
        self.controle.append(cc)
        cc.start()
        idCliente += 1
    except:
      exit(0)

  def encerrar(self):
    print("[...] Encerrando thread controleAccept...")
    self.sock.shutdown(0)
    self.sock.close()
    print("[XXX] Thread controleAccept encerrada.")

class ControleCliente(Thread):
  """
  Thread : gerencia o cliente e sua interacão com o servidor.
  Mantendo ele conectado a estação escolhida.
  """

  def __init__(self, idCliente, sock, addrCliente, estacoes):
    self.idCliente = idCliente
    self.sock      = sock
    self.addrCliente = addrCliente
    self.estacoes    = estacoes
    Thread.__init__(self)

  def run(self):
    try:
      portaUdp = self.__receberHello()

      print("\n[<==] Hello recebido de ", self.addrCliente)

      self.__enviarWelcome()

      numEstacao = self.__receberSetStation()
      print("[<==] SetStation recebido de ", self.addrCliente)

      self.enviarAnnounce(self.estacoes[numEstacao].arquivo[:-4])  # retira o '.mp3'

      self.cliente = Cliente(self.idCliente, self.addrCliente, self.sock, portaUdp, numEstacao, self)

      self.__addClienteEstacao(numEstacao, self.cliente)
      print("[...] Cliente adicionado a estação ", numEstacao)

      while True:
        novoNumEstacao = self.__receberSetStation()

        print("[<==] SetStation recebido de ", self.addrCliente)
        print("[...] realizando troca de estação... ", self.addrCliente)
        self.__rmClienteEstacao(numEstacao, self.cliente)
        self.__addClienteEstacao(novoNumEstacao, self.cliente)
        print("[...] troca feita com sucesso ", self.addrCliente)
        self.enviarAnnounce(self.estacoes[novoNumEstacao].arquivo[:-4])  # retira o '.mp3'
    except:
      exit(0)

  def __enviarWelcome(self):
    """
    Protocolo: envia um welcome e espera receber um SetStation.
    Retorna o 'número da estação' recebido ou '-1' caso contrario.
    """
    tipoComando = hton(Comandos.welcome)
    numEstacoes = hton(len(self.estacoes), False)

    self.sock.send(tipoComando)
    self.sock.send(numEstacoes)
    print("[==>] Welcome enviado para ", self.addrCliente)
    print("[==>] Welcome número de estações ", len(self.estacoes))

  def enviarAnnounce(self, nomeMusica):
    """Protocolo"""
    print("[==>] announce para ", self.addrCliente)
    typeCommand = hton(Comandos.announce)
    songNameSize = hton(len(nomeMusica))
    print("[==>] songNameSize ", ntoh(songNameSize, False))
    print("[==>] SongName '", nomeMusica, "'")
    songName = hton(nomeMusica)

    self.sock.send(typeCommand)
    self.sock.send(songNameSize)
    self.sock.send(songName)
  
  def __receberHello(self):
    tipoComando = ntoh(self.sock.recv(1), False)
    portaUdp = ntoh(self.sock.recv(2), False)

    if tipoComando != Comandos.hello:
      self.__exitComandoInvalido("Era esperado um Hello.")

    return portaUdp

  def __receberSetStation(self):
    tipoComando = ntoh(self.sock.recv(1), False)
    numEstacao = ntoh(self.sock.recv(2), False)

    if tipoComando != Comandos.setStation:
      self.__exitComandoInvalido("Era esperado um SetStation")
    elif numEstacao < 0 or numEstacao >= len(self.estacoes):
      self.__exitComandoInvalido("Número da estação inválido")

    return numEstacao

  def __addClienteEstacao(self, numEstacao, cliente):
    if not self.estacoes[numEstacao].status:
      self.estacoes[numEstacao].status = True
      self.estacoes[numEstacao].start()

    self.estacoes[numEstacao].addCliente(cliente)

  def __rmClienteEstacao(self, numEstacao, cliente):
    self.estacoes[numEstacao].rmCliente(cliente)

  def __exitComandoInvalido(self, msg):
    """Protocolo"""
    print("[<==] Comando inválido de ", self.addrCliente)
    print("[==>] Enviando InvalidCommand para ", self.addrCliente)

    typeCommand = hton(Comandos.invalidCommand)
    replyStringSize = hton(len(msg))
    replyString = hton(msg)

    print("[==>] replyString: ", msg)
    
    self.sock.send(typeCommand)
    self.sock.send(replyStringSize)
    self.sock.send(replyString)
  
    print("[=x>] Desconectando cliente ", self.addrCliente)
    self.sock.close()
    print("[<x>] Cliente", self.addrCliente, " desconectado.")
    self.estacoes[self.cliente.numEstacao].rmCliente(self.cliente)
    self.encerrar()
    # exit(-1)
  
  def encerrar(self):
    print("[...] Encerrando conexão com ", self.addrCliente)
    self.sock.shutdown(0)
    self.sock.close()
    print("[<x>] Conexão encerrada com ", self.addrCliente)
    self.estacoes[self.cliente.numEstacao].rmCliente(self.cliente)

class ConexaoServidor(Thread):
  """
  Thread: gerencia a conexao do cliente com o servidor.
  Recebe os comandos do protolo e processa eles.
  """

  def __init__(self, sock, portaUdp, enderecoServidor):
    self.sock     = sock
    self.portaUdp = portaUdp
    self.enderecoServidor = enderecoServidor
    Thread.__init__(self)

  def run(self):
    try:
      self.enviarHello()

      while True:
        commandType = ntoh(self.sock.recv(1), False)

        if commandType == Comandos.invalidCommand:
          print("\n[<==] Invalid Command recebido de ", self.enderecoServidor)
          replyStringSize = ntoh(self.sock.recv(1), False)
          replyString = ntoh(self.sock.recv(replyStringSize) , True)

          print("[<==] replyString '", replyString, "'")
          print("[...] close: fechando socket...")
          self.sock.close()
          print("[<x>] close: socket fechado.")
          exit(-1)
        
        if commandType == Comandos.welcome:
          print("\n[<==] Welcome recebido de ", self.enderecoServidor)
          numStations = ntoh(self.sock.recv(2), False)
          print("[<==] Número de estações : 1 -", numStations)
        
        elif commandType == Comandos.announce:
          print("\n[<==] Announce recebido de ", self.enderecoServidor)
          songNameSize = ntoh(self.sock.recv(1), False)
          print("[<==] songNameSize ", songNameSize)
          songName = ntoh(self.sock.recv(songNameSize), True)
          print("[<==] Música atual: '", songName, "'")

    except:
      exit(0)

  def enviarHello(self):
    """
    Protoco: enviar um Hello para o SERVIDOR com a porta do cliente UDP.
    """
    commandType = hton(Comandos.hello)
    portaUdp = hton(self.portaUdp, False)

    self.sock.send(commandType)
    self.sock.send(portaUdp)
    print("[==>] Hello enviado para ", self.enderecoServidor)

  def enviarSetEstation(self, stationNumber):
    """
    Protoco: enviar um SetEstation para o SERVIDOR com o número de estação escolhido.
    """
    commandType = hton(Comandos.setStation)
    stationNumber = hton(stationNumber, False)

    self.sock.send(commandType)
    self.sock.send(stationNumber)
    print("[==>] SetStation enviado para ", self.enderecoServidor)

  def encerrarConecao(self):
    print("[...] Encerrando conexão com ", self.enderecoServidor)
    self.sock.shutdown(0)
    self.sock.close()
    print("[<x>] Conexão encerrada com ", self.enderecoServidor)

def criarThreadsEstacoes(listaArquivos, readingSize=4096):
  """
  Recebe uma lista com os arquivos das musica
  Retorno uma lista :
      index = chave 0 até (N-1) onde N é número de arquivos
      value = Estacao()
  """
  threadsEstacoes = []
  for index, arquivo in enumerate(listaArquivos):
    threadsEstacoes.append(Estacao(index, arquivo, readingSize=readingSize))
  return threadsEstacoes

def ntoh(dados, isStr):
  """
  Converte os bytes recebidos pela rede em números inteiros ou strings.
  Byteorder e dependente do sistema.
  """
  if isStr:
    return dados.decode()
  return int().from_bytes(dados, byteorder=sbyteorder)

def hton(dados, is8bits=True):
  """
  Converte os números inteiros em em tipos semelhante aos da liguagem C e strings 
  para serem enviados pela rede.
  """
  if type(dados) == str:
    return dados.encode()

  if is8bits:
    return c_uint8(dados)
  
  return c_uint16(dados)
