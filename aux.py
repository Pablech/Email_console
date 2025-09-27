import os
import re
import readline
import sys
from getpass import getpass as g
from typing import Any

import bcrypt

from data_base import DataBase


class Hash_Pass:
    """
    Gerencia a criptografia e verificação de senhas usando o algoritmo bcrypt.

    Esta classe oferece métodos para transformar senhas em texto puro em
    hashes seguros e para comparar uma senha digitada com um hash armazenado.
    """

    def __init__(self):
        """
        Inicializa a classe.

        Neste caso, o construtor é vazio, pois os métodos são independentes
        do estado da instância.
        """
        pass

    def hash_senha(self, senha: str) -> str:
        """
        Gera um hash seguro de uma senha usando bcrypt.

        O processo inclui a geração de um 'salt' aleatório, que é uma string
        única que garante que senhas iguais tenham hashes diferentes,
        aumentando a segurança.

        Args:
            senha (str): A senha em texto puro a ser criptografada.

        Returns:
            str: O hash da senha em formato de string.
        """
        # Converte a senha de string (str) para bytes (b'), pois bcrypt
        # trabalha com este tipo de dado.
        senha_bytes = senha.encode('utf-8')

        # Gera um 'salt' e cria o hash da senha. O gensalt() é responsável
        # por adicionar a complexidade e aleatoriedade.
        hashed_senha = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

        # Converte o hash de bytes de volta para string para que possa ser
        # facilmente armazenado em um banco de dados.
        return hashed_senha.decode('utf-8')

    @staticmethod
    def verifica_senha(senha: str, hashed_senha: str) -> bool:
        """
        Verifica se a senha digitada corresponde ao hash armazenado.

        Este método não precisa de uma instância da classe, por isso é
        definido como @staticmethod.

        Args:
            senha (str): A senha em texto puro digitada pelo usuário.
            hashed_senha (str): O hash da senha armazenado no banco de dados.

        Returns:
            bool: True se as senhas corresponderem, False caso contrário.
        """
        # Converte a senha em texto puro para bytes.
        senha_bytes = senha.encode('utf-8')

        # Converte o hash armazenado para bytes, pois a função checkpw
        # espera este formato.
        hashed_bytes = hashed_senha.encode('utf-8')

        # Compara a senha digitada com o hash armazenado.
        # O próprio bcrypt.checkpw() se encarrega de extrair o 'salt' do
        # hash e fazer a verificação corretamente.
        return bcrypt.checkpw(senha_bytes, hashed_bytes)


def senha(mensagem):
    """
    Solicita uma senha ao usuário de forma segura.

    Esta função usa `getpass` (aqui renomeada para 'g') para ler a senha
    diretamente do console sem exibir os caracteres digitados.

    Returns:
        str: A senha digitada pelo usuário.
    """
    senha = g(mensagem)
    return senha


def encerra_programa(comando, banco):
    """
    Encerra o programa se o comando for 'quik'.

    Esta função verifica se o comando fornecido é 'quik'. Se for, ela fecha
    a conexão com o banco de dados e encerra a execução do script
    e apaga os arquivos html gerados.

    Args:
        comando (str): O comando fornecido pelo usuário.
        banco (objeto): Uma instância de uma classe de banco de dados
                        que possui um método `fecha_cnx()`.
    """
    if comando == 'quik':
        banco.fecha_cnx()
        os.system('del email_id_*' if os.name == 'nt' else 'rm email_id_*')
        print('programa encerrado')
        sys.exit(0)


def limpa():
    """
    Limpa o console do terminal.

    Verifica o sistema operacional para usar o comando correto: 'cls' para
    Windows ('nt') ou 'clear' para sistemas baseados em Unix, como Linux ou macOS.
    """
    os.system('cls' if os.name == 'nt' else 'clear')


class Autocomplete:
    """
    Gerencia o autocompletar da linha de comando usando a tecla TAB.

    Esta classe integra-se com o módulo 'readline' para fornecer
    funcionalidades de autocompletar para comandos, contatos e caminhos
    de arquivos.
    """
    __completados: list[Any]
    __data_base: DataBase

    def __init__(self, data_base: DataBase):
        """
        Inicializa a classe Autocomplete.

        Args:
            data_base (DataBase): Uma instância da classe DataBase, usada
                                  para buscar comandos e contatos.
        """
        self.__completados = []
        self.__data_base = data_base
        self.__configura_tab()

    def __configura_tab(self):
        """
        Configura o módulo readline para habilitar o autocompletar.

        Define a função de autocompletar, habilita a tecla TAB para o comando
        'complete' e configura os delimitadores para a divisão da entrada.
        """
        readline.set_completer(self.__complete)
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(' ')

    def __complete(self, entrada: str, estado: int):
        """
        Método principal de autocompletar, chamado pelo readline.

        Este método é a lógica central que gera as sugestões de
        autocompletar. Ele busca por comandos, contatos ou caminhos de
        arquivos dependendo da entrada do usuário.

        Args:
            entrada (str): O texto digitado pelo usuário na linha de comando.
            estado (int): Um índice que indica qual sugestão deve ser
                          retornada. O valor 0 indica a primeira busca.

        Returns:
            str | None: A próxima sugestão de autocompletar ou None se
                        não houver mais sugestões.
        """
        if estado == 0:
            self.__completados.clear()
            if '/' in entrada:
                try:
                    caminho_base = os.path.dirname(entrada) if os.path.dirname(entrada) else '.'
                    nome_arquivo = os.path.basename(entrada)
                    sugestoes_arquivos = []
                    for item in os.listdir(caminho_base):
                        if item.startswith(nome_arquivo):
                            caminho_completo = os.path.join(caminho_base, item)
                            sugestoes_arquivos.append(caminho_completo)
                    if sugestoes_arquivos:
                        self.__completados.extend(sorted(sugestoes_arquivos))
                        try:
                            return self.__completados[estado] + '/'
                        except Exception:
                            return None
                except FileNotFoundError:
                    return None
            else:
                self.__completados.extend(self.__data_base.busca_cmds(entrada))
                self.__completados.extend(self.__data_base.busca_contatos(entrada))
        try:
            return self.__completados[estado] + ' '
        except Exception:
            return None


class Entrada:
    """
    Gerencia a entrada de dados do usuário e a interpreta como comandos.

    Esta classe é responsável por ler a entrada do usuário a partir do terminal,
    analisar os argumentos no formato 'chave=valor' e armazenar os dados
    separadamente em atributos da classe.
    """

    def __init__(self):
        """
        Inicializa uma nova instância da classe Entrada.

        Define todos os atributos de comando e dados como None ou listas vazias.
        """
        self.__entrada = None
        self.__comando = None
        self.__contatos = []
        self.__indice = None
        self.__assunto = None
        self.__mensagem = None
        self.__arquivos = []
        self.__query = None
        self.__limit = None
        self.__user = None

    def __filtra_entrada(self):
        """
        Analisa a string de entrada do usuário para extrair comandos e argumentos.

        Este método privado divide a entrada em pares 'chave=valor' e atribui os
        valores aos atributos internos da classe. A lógica prioriza a detecção de
        comandos como 'show', 'search', etc., antes de 'send'.
        """

        args = {}

        partes = re.findall(r'(\S+)=\s*(.*?)(?=\s\S+=|$)', self.__entrada)

        for parte in partes:
            if parte:
                chave, valor = parte
                valor = valor.strip()
                args[chave] = valor

        if 'show' in args:
            self.__comando = 'show'
            self.__indice = args.get('show')
        elif 'search' in args:
            self.__comando = 'search'
            self.__query = args.get('search')
            self.__limit = args.get('limit')
        elif 'back' in args:
            self.__comando = 'back'
        elif 'quik' in args:
            self.__comando = 'quik'
        elif 'help' in args:
            self.__comando = 'help'
        elif 'prev' in args:
            self.__comando = 'prev'
        elif 'next' in args:
            self.__comando = 'next'
        elif 'user' in args:
            self.__comando = 'user'
            self.__user = args.get('user')
        elif 'send' in args:
            self.__comando = 'send'
            emails_str = args.get('send', '')
            if emails_str:
                self.__contatos = emails_str.split()

            self.__assunto = args.get('ass', '')
            self.__mensagem = args.get('msg', '')

            arquivos_str = args.get('file', '')
            if arquivos_str:
                self.__arquivos = [f.rstrip('/') for f in arquivos_str.split()]
            else:
                self.__comando = None

    def entrada(self, mensagem: str):
        """
        Solicita e lê a entrada do usuário a partir do terminal.

        O texto lido é armazenado no atributo interno __entrada.

        Args:
            mensagem (str): A mensagem a ser exibida como prompt para o usuário.
        """
        while True:
            try:
                self.__entrada = input(mensagem)
                # Chama a função para filtrar a entrada
                self.__filtra_entrada()
                break
            except KeyboardInterrupt:
                print('quik= para sair')

    @property
    def usuario(self):
        """
        Retorna o nome de usuário

        :return:
            str: O nome de usuário
        """
        return self.__user

    @property
    def limite(self) -> int:
        """
        Retorna o limite de e-mails s serem buscados.

        Returns:
            int: O limite de e-mails a serem buscados, convertido para inteiro.
        """
        if self.__limit:
            return int(self.__limit)
        return 50

    @property
    def query(self) -> str | None:
        """
        Retorna a query de busca extraída da entrada.

        Returns:
            str | None: A query de busca, se houver, ou None.
        """
        return self.__query

    @property
    def assunto(self) -> str | None:
        """
        Retorna o assunto extraído da entrada.

        Returns:
            str | None: O assunto, se houver, ou None.
        """
        return self.__assunto

    @property
    def contatos(self) -> list[str]:
        """
        Retorna a lista de e-mails de contato extraída da entrada.

        Returns:
            list[str]: Uma lista de strings com os endereços de e-mail.
        """
        return self.__contatos

    @property
    def indice(self) -> int:
        """
        Retorna o índice para visualização de e-mail.

        Returns:
            int: O índice do e-mail, convertido para inteiro.
        """
        return int(self.__indice)

    @property
    def comando(self) -> str | None:
        """
        Retorna o comando principal identificado na entrada.

        Returns:
            str | None: O comando ('show', 'search', etc.), ou None.
        """
        return self.__comando

    @property
    def mensagem(self) -> str | None:
        """
        Retorna o corpo da mensagem extraído da entrada.

        Returns:
            str | None: A mensagem, se houver, ou None.
        """
        return self.__mensagem

    @property
    def arquivos(self) -> list[str]:
        """
        Retorna a lista de caminhos de arquivos extraída da entrada.

        Returns:
            list[str]: Uma lista de strings com os caminhos dos arquivos.
        """
        return self.__arquivos

    def ajuda(self):
        """
        Imprime uma mensagem de ajuda no console com a sintaxe dos comandos.
        """
        ajuda = (
            '\nsend= {email@1 email@2} (1 ou mais) ass= OPCIONAL msg= OPCIONAL file= caminho para o arquivo OPCIONAL\n'
            '\nshow= {N} (N é o indice do email a ser aberto)\n'
            '\nsearch= query de busca gmail ex: is:uread (para não lidos) limit= N limite de busca OPCIONAL (padrão 50)\n'
            '\nuser= {usuario}\n'
            '\n{campos obrigatórios}\n'
            '\nprev= página previa de exibição\n'
            '\nnext= próxima página de exibição\n'
            '\nback= para voltar\n'
            '\nquik= para sair a qualquer momento (Ctrl + c desativado em inputs)\n'
            '\nhelp= para ver esta mensagem\n')
        print(ajuda)
