import mysql.connector

import aux
import data_base
import gmail_server

de = 'padagoec@gmail.com'


def imprime_emails(buscados):
    """
    Exibe uma lista de e-mails de forma paginada e interage com o usuário.

    Permite que o usuário navegue entre as páginas de resultados ('next', 'prev'),
    abra um e-mail específico ('show') ou retorne ao menu principal ('back').

    Args:
        buscados (list): Uma lista de objetos de e-mail a serem exibidos.
    """

    pag_atual = 0
    tam_pag = 10

    while True:
        # Calcula o índice de início e fim da página atual
        inicio = pag_atual * tam_pag
        fim = inicio + tam_pag
        # Verifica se há e-meils encontrados
        if not buscados:
            return 


        exibir = buscados[inicio:fim]

        # Se não houver e-mails na fatia, significa que chegou ao fim da lista.
        if not exibir:
            return

        # Exibe os e-mails da página atual
        for i, email_ in enumerate(exibir):
            print(f'{inicio + i + 1} - {email_}')

        entrada.entrada('\ninbox@[show=]~ ')
        comando = entrada.comando
        if comando:
            aux.encerra_programa(comando, db_instance)
            if comando == 'back':
                break
            elif comando == 'next':
                # Verifica se há mais páginas antes de avançar
                if fim < len(buscados):
                    pag_atual += 1
                else:
                    print('\a\nNão há mais paginas\n')
            elif comando == 'prev':
                # Verifica se não está na primeira página antes de voltar
                if pag_atual > 0:
                    pag_atual -= 1
                else:
                    print('\a\nJá está na primeira página\n')
            elif comando == 'show':
                index = entrada.indice
                try:
                    index = int(index)
                except ValueError:
                    print(f'Error: {index} inválido')
                    continue
                # Converte o índice exibido para o índice real na lista 'buscados'
                index = index - 1
                if 0 <= index < len(buscados):
                    cache.open_html(buscados[index])
                else:
                    print('\a\nIndex error\n')
            elif comando == 'help':
                entrada.ajuda()
            else:
                print(f'\aError: <{comando}>')


def valida_data_base():
    """
    Tenta se conectar ao banco de dados com a senha fornecida pelo usuário.
    Continua pedindo a senha até que a conexão seja bem-sucedida.

    Returns:
        data_base.DataBase: Uma instância do banco de dados se a conexão
                            for bem-sucedida.
    """
    while True:
        try:
            db_pass = aux.senha('\njoin@[db_passwd]~ ')
            db_instance = data_base.DataBase(db_pass)
            return db_instance
        except mysql.connector.Error as error:
            print(f'\nError: {error}')


def login_ou_cadastro(db_instance, entrada):
    """
    Gerencia o processo de login ou criação de novo usuário.

    Args:
        db_instance (data_base.DataBase): Instância do banco de dados.
        entrada (aux.Entrada): Instância para entrada de dados.

    Returns:
        bool: Retorna True se o login for bem-sucedido, False se o processo for cancelado.
    """
    hash_pass = aux.Hash_Pass()

    if db_instance.verifica_tabela_login():
        while True:
            entrada.entrada('login@[user=login]~ ')
            comando = entrada.comando
            aux.encerra_programa(comando, db_instance)

            if comando == 'user':
                usuario = entrada.usuario
                passwd_hash = db_instance.busca_login(usuario)
                if passwd_hash:
                    passwd = aux.senha('login@[passwd=passwd]~ ')
                    if hash_pass.verifica_senha(passwd, passwd_hash):
                        return True
                    else:
                        print('\aSenha incorreta.')
                else:
                    print('\aUsuário não encontrado.')
    else:
        while True:
            entrada.entrada('new-acc@[user=new]~ ')
            comando = entrada.comando
            aux.encerra_programa(comando, db_instance)

            if comando == 'user':
                usuario = entrada.usuario
                while True:
                    new_pass = aux.senha('new-acc@[passwd=new]~ ')
                    check_pass = aux.senha('new-acc@[passwd=check]~ ')
                    if new_pass == check_pass:
                        hashed_pass = hash_pass.hash_senha(new_pass)
                        db_instance.salva_login(usuario, hashed_pass)
                        return True
                    else:
                        print('\aInválido: new != check')


def main(cache, client, db_instance, entrada):
    """
    Loop principal da aplicação que gerencia a interação com o usuário.

    Oferece opções para enviar e-mails, buscar e-mails e obter ajuda.

    Args:
        cache (Email_Cache): Instância do cache de e-mails.
        client (EmailClient): Instância do cliente de e-mail.
        db_instance (DataBase): Instância do banco de dados para contatos.
        entrada (Entrada): Instância para gerenciar a entrada do usuário.
    """
    while True:
        entrada.entrada('\nmain@[main]~ ')
        aux.encerra_programa(entrada.comando, db_instance)
        comando = entrada.comando
        if comando:
            if comando == 'send':
                para = entrada.contatos
                if para:
                    ass = entrada.assunto
                    msg = entrada.mensagem
                    arqvs = entrada.arquivos
                    print(para, ass, msg, arqvs)
                    msgs = client.write_email(para, ass, msg, arqvs)
                    send = input(
                        f'Mensagem:\npara: {para}\nassunto: {ass}\nmensagem: {msg}\narquivos: {arqvs}\n(S/*): ').strip()
                    if send == 'S':
                        db_instance.salva_contatos(para)
                        client.send_email(msgs)
                else:
                    print('\aDestinatário nescesário')
            elif comando == 'search':
                query = entrada.query
                limite = entrada.limite
                try:
                    limite = int(limite)
                except ValueError:
                    print(f'Error: {limite} inválido')
                    continue
                buscados = cache.search_emails(limite, query)
                imprime_emails(buscados)
            elif comando == 'help':
                entrada.ajuda()
            else:
                print(f'\nComando <{comando}> incorreto')


if __name__ == '__main__':
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    entrada = aux.Entrada()

    # Valida a conexão com o banco de dados uma única vez
    db_instance = valida_data_base()
    aux.Autocomplete(db_instance)

    # Tenta o login ou a criação de usuário
    if login_ou_cadastro(db_instance, entrada):
        email = gmail_server.Email()
        """esta com erro aqui"""
        cache = gmail_server.Email_Cache()
        client = gmail_server.EmailClient(email)
        cache.set_service(client)
        client.set_cache_clas(cache)
        main(cache, client, db_instance, entrada)
