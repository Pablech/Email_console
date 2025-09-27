import mysql.connector  # Conector para interagir com o banco de dados MySQL/MariaDB


class DataBase:
    """
    Gerencia a conexão e as operações com um banco de dados MySQL/MariaDB.

    A classe é responsável por:
    - Conectar e criar o banco de dados e as tabelas necessárias.
    - Realizar buscas e salvamento de comandos, contatos e dados de login.
    - Garantir que as operações sejam seguras e robustas.
    """

    # Nomes de tabelas e colunas para manter a consistência e facilitar a manutenção
    __db_tabela_cmds = 'comandos'
    __db_coluna_cmds = 'cmds'
    __db_tabela_contatos = 'contatos'
    __db_coluna_email = 'emails'
    __db_tabela_login = 'login'
    __db_coluna_usuario = 'usuario'
    __db_coluna_senha = 'senha'

    def __init__(self, db_pass):
        """
        Inicializa a classe, definindo credenciais e conectando ao banco de dados.
        """
        self.__db_host = 'localhost'
        self.__db_user = 'root'
        self.__db_name = 'sistema'
        self.__db_pass = db_pass

        self.__cnx = None

        # # Tenta estabelecer a conexão com o banco de dados
        self.__conecta_db()

        # Se a conexão for bem-sucedida, cria as tabelas
        if self.__cnx:
            self.__cria_tabela_contatos()
            self.__cria_tabela_cmds()
            self.__cria_tabela_login()

    def __conecta_db(self):
        """
        Tenta conectar ao banco de dados. Se o banco não existir, ele é criado
        e a conexão é restabelecida.

        Returns:
            bool: Retorna True se a conexão for bem-sucedida, False caso contrário.
        """
        try:
            # Primeira tentativa de conexão
            self.__cnx = mysql.connector.connect(
                host=self.__db_host,
                user=self.__db_user,
                passwd=self.__db_pass,
                database=self.__db_name
            )
            return True

        except mysql.connector.Error:
            # Se o erro for o banco de dados não existir
            try:
                # Conecta ao servidor para criar o banco de dados
                temp_cnx = mysql.connector.connect(
                    host=self.__db_host,
                    user=self.__db_user,
                    passwd=self.__db_pass
                )
            except mysql.connector.errors.ProgrammingError as proerr:
                # Trata erros na segunda tentativa de conexão ou criação
                # Retorna ao início para solicitar outra senha
                raise proerr
            except mysql.connector.Error as error:
                # Trata erros de forma genêrica
                raise error

            temp_cursor = temp_cnx.cursor()
            temp_cursor.execute(f"CREATE DATABASE {self.__db_name}")
            temp_cursor.close()
            temp_cnx.close()

            # Se a tentativa de conecção a um banco genêrico for bem sucedida,
            # retorna à função para uma nova tentativa de conecção ao banco do sistema
            return self.__conecta_db()

    def __carrega_cmds(self):
        """
        Popula a tabela de comandos com uma lista de comandos padrão.
        """
        cmds = ['send=', 'show=', 'search=', 'back=', 'quik=', 'help=', 'file=', 'limit=', 'ass=', 'msg=', 'file=',
                'next=', 'prev=', 'user=']
        try:
            with self.__cnx.cursor() as cursor:
                # Usa INSERT IGNORE para evitar duplicatas
                query = f'INSERT IGNORE INTO `{self.__db_tabela_cmds}` ({self.__db_coluna_cmds}) VALUES (%s);'
                data = [(cmd,) for cmd in cmds]
                cursor.executemany(query, data)
                self.__cnx.commit()
        except mysql.connector.Error:
            pass

    def busca_contatos(self, contato):
        """
        Busca contatos no banco de dados com base em uma string de busca.
        """
        busca = []
        try:
            with self.__cnx.cursor() as cursor:
                query = f'SELECT {self.__db_coluna_email} FROM {self.__db_tabela_contatos} WHERE {self.__db_coluna_email}  LIKE %s LIMIT 50;'
                cursor.execute(query, (contato + '%',))

                for row in cursor.fetchall():
                    busca.append(row[0])
        except mysql.connector.Error:
            pass
        return busca

    def busca_cmds(self, cmds):
        """
        Busca comandos no banco de dados.
        """
        busca = []
        with self.__cnx.cursor() as cursor:
            query = f'SELECT {self.__db_coluna_cmds} FROM {self.__db_tabela_cmds} WHERE {self.__db_coluna_cmds} LIKE %s LIMIT 50;'
            cursor.execute(query, (cmds + '%',))

            for row in cursor.fetchall():
                busca.append(row[0])
        return busca

    def __inicia_tabela_cmds(self):
        """
        Verifica se a tabela de comandos está vazia e a popula se necessário.
        """
        teste = self.busca_cmds('send=')
        if not teste:
            self.__carrega_cmds()

    def salva_contatos(self, novos):
        """
        Salva novos contatos no banco de dados, evitando duplicatas.
        """
        if not novos:
            return None
        try:
            with self.__cnx.cursor() as cursor:
                for novo in novos:
                    teste = self.busca_contatos(novo)
                    if not teste:
                        cursor.execute(
                            f'INSERT INTO `{self.__db_tabela_contatos}` ({self.__db_coluna_email}) VALUES (%s);',
                            (novo,))
                        self.__cnx.commit()
        except mysql.connector.Error:
            pass

    def salva_login(self, usuario, senha):
        """
        Salva um novo usuário e senha no banco de dados.
        """
        if not usuario or not senha:
            return None
        try:
            with self.__cnx.cursor() as cursor:
                query = f'INSERT INTO `{self.__db_tabela_login}` ({self.__db_coluna_usuario}, {self.__db_coluna_senha}) VALUES (%s, %s);'
                cursor.execute(query, (usuario, senha))
                self.__cnx.commit()
        except mysql.connector.Error:
            pass

    def verifica_tabela_login(self):
        """
        Verifica se a tabela de login está populada com algum registro.

        A função executa uma consulta SQL para contar o número de linhas na
        tabela de login. Se a contagem for maior que zero, a tabela contém dados.

        Returns:
            bool: Retorna True se a tabela tiver registros,
                  retorna False se a tabela estiver vazia.
        """
        try:
            with self.__cnx.cursor() as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM {self.__db_tabela_login};')
                resultado = cursor.fetchone()
                contagem = resultado[0]
                return contagem > 0
        except mysql.connector.Error:
            pass

    def busca_login(self, usuario):
        """
        Busca a senha de um usuário no banco de dados.
        """
        if not usuario:
            return None
        with self.__cnx.cursor() as cursor:
            query = f'SELECT {self.__db_coluna_senha} FROM {self.__db_tabela_login} WHERE {self.__db_coluna_usuario} = %s'
            cursor.execute(query, (usuario,))
            senha = cursor.fetchone()
            if senha:
                return senha[0]
        return None

    def __cria_tabela_login(self):
        """
        Cria a tabela de 'login' se ela ainda não existir.
        """
        try:
            with self.__cnx.cursor() as cursor:
                cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.__db_tabela_login} (
                        id INT UNIQUE DEFAULT 1,
                        {self.__db_coluna_usuario} VARCHAR(100) NOT NULL UNIQUE,
                        {self.__db_coluna_senha} VARCHAR(100) NOT NULL
                    );''')
        except mysql.connector.Error:
            pass

    def __cria_tabela_cmds(self):
        """
        Cria a tabela de 'comandos' se ela ainda não existir e a popula.
        """
        try:
            with self.__cnx.cursor() as cursor:
                cursor.execute(f'''CREATE TABLE IF NOT EXISTS `{self.__db_tabela_cmds}` (
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                    {self.__db_coluna_cmds} VARCHAR(15) NOT NULL UNIQUE
                    );''')
                self.__inicia_tabela_cmds()
        except mysql.connector.Error:
            pass

    def __cria_tabela_contatos(self):
        """
        Cria a tabela de 'contatos' se ela ainda não existir.
        """
        try:
            with self.__cnx.cursor() as cursor:
                cursor.execute(f'''CREATE TABLE IF NOT EXISTS `{self.__db_tabela_contatos}` (
                    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                    {self.__db_coluna_email} VARCHAR(50) NOT NULL UNIQUE
                    );''')
        except mysql.connector.Error:
            pass

    def fecha_cnx(self):
        """
        Fecha a conexão com o banco de dados se ela estiver aberta.
        """
        if self.__cnx and self.__cnx.is_connected():
            self.__cnx.close()
