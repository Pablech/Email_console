import base64
import email
import email.encoders
import itertools
import mimetypes
import os
import pickle
import webbrowser
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define o ID do usuário como 'me', que representa o usuário autenticado.
id_usuario = 'me'


class Email:
    """
    Representa um e-mail com seus dados extraídos da API do Gmail.

    Esta classe atua como um objeto de valor (value object) para encapsular
    as propriedades de um e-mail, como ID, remetente, assunto, e conteúdo,
    proporcionando acesso simplificado a esses dados.
    """

    def __init__(self, email_data=None):
        """
        Inicializa uma nova instância da classe Email.

        Args:
            email_data (dict): Um dicionário contendo os dados do e-mail.
        """
        # Atribui os dados do dicionário a atributos privados, usando .get()
        # para evitar erros caso a chave não exista.
        if email_data:
            self.__id = email_data.get('id', '')
            self.__assunto = email_data.get('assunto', '')
            self.__remetente = email_data.get('remetente', '')
            self.__destinatario = email_data.get('destinatario', '')
            self.__data = email_data.get('data', '')
            self.__corpo_texto = email_data.get('corpo_texto', '')
            self.__corpo_html = email_data.get('corpo_html', '')
            self.__anexos = email_data.get('anexos', [])

    def __str__(self):
        """
        Retorna uma representação em string do e-mail para exibição.
        """
        return f'De: {self.__remetente} | Assunto: {self.__assunto}'

    @property
    def id_(self):
        """Retorna o ID único do e-mail."""
        return self.__id

    @property
    def assunto(self):
        """Retorna o assunto do e-mail."""
        return self.__assunto

    @property
    def remetente(self):
        """Retorna o remetente do e-mail."""
        return self.__remetente

    @property
    def destinatario(self):
        """Retorna o destinatário do e-mail."""
        return self.__destinatario

    @property
    def data(self):
        """Retorna a data de envio do e-mail."""
        return self.__data

    @property
    def corpo_texto(self):
        """Retorna o corpo do e-mail em formato de texto simples."""
        return self.__corpo_texto

    @property
    def corpo_html(self):
        """Retorna o corpo do e-mail em formato HTML."""
        return self.__corpo_html

    @property
    def anexos(self):
        return self.__anexos


class Email_Cache:
    """
    Gerencia um cache local de e-mails para otimizar operações.

    Esta classe armazena e-mails já visualizados ou buscados, evitando
    chamadas repetidas à API do Gmail. Ela implementa lógicas de busca
    local e remota, dependendo da query e do estado do cache.
    """

    def __init__(self):
        """
        Inicializa a instância do cache de e-mails.

        Args:
        """
        # Armazena o cliente de e-mail e o ID do usuário.
        self.__service = None
        self.__id_usuario = id_usuario
        # Lista para armazenar objetos de e-mail.
        self.__emails_list = []
        # Lista para armazenar as queries de busca já executadas.
        self.__querys_list = []
        # Conjunto para armazenar IDs de e-mail para uma busca rápida de duplicatas.
        self.__emails_ids_set = set()

    def set_service(self, service):
        """
        :param service: Instância de EmailClient
        """
        self.__service = service

    def open_html(self, email):
        """
        Gera e abre um arquivo HTML com o conteúdo do e-mail no navegador.

        Args:
            email (object): Objeto Email a ser aberto no navegador.
        """
        # Obtém o conteúdo HTML do e-mail.
        html_email = self.__get_content_html(email)

        # Se o conteúdo HTML não puder ser extraído, imprime um erro e retorna.
        if not html_email:
            print('\aErro ao extrairo o html')
            return

        # Define o nome do arquivo HTML.
        nome_arquivo = f'email_id_{email.id_}.html'
        try:
            # Cria e escreve o conteúdo HTML no arquivo.
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(html_email)

            # Abre o arquivo HTML no navegador web padrão.
            webbrowser.open('file://' + os.path.realpath(nome_arquivo))
        except Exception as error:
            print(f'\aError ao abrir HTML: {error}')

    def __get_content_html(self, email_data):
        """
        Gera o conteúdo HTML completo para a visualização de um e-mail.

        Args:
            email_data (objeto): Objeto da classe Email.

        Returns:
            str: Uma string HTML contendo o e-mail formatado.
        """

        # Inicia a construção da string HTML com a estrutura básica.
        html_content = """
            <!DOCTYPE html>
            <html lang="pt-br">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Visualização do E-mail</title>
                <style>
                    # O bloco <style> contém CSS para estilizar a página HTML.
                    # Ele define o estilo da fonte, cores, espaçamento e layout
                    # para uma visualização limpa e moderna do e-mail.
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 20px; line-height: 1.6; background-color: #f4f4f9; color: #333; }}
                    .container {{ max-width: 800px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                    h1 {{ color: #0056b3; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                    pre {{ background: #352f2f; padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }}
                    .header-info {{ margin-bottom: 20px; }}
                    .header-info p {{ margin: 5px 0; }}
                    .attachments {{ margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header-info">
                        <p><strong>De:</strong> {remetente}</p>
                        <p><strong>Para:</strong> {destinatario}</p>
                        <p><strong>Data:</strong> {data}</p>
                    </div>
                    <h1>{assunto}</h1>
                    <hr>
                    <div>
                        # Este é o corpo principal do e-mail.
                        # A expressão 'if/else' em uma linha verifica se existe um corpo HTML.
                        # Se sim, usa-o. Se não, formata o corpo de texto simples dentro de
                        # uma tag <pre> para manter a formatação original (quebras de linha, espaços).
                        {corpo_email}
                    </div>
            """.format(
            # Formata a string com os dados do e-mail.
            assunto=email_data.assunto,
            remetente=email_data.remetente,
            destinatario=email_data.destinatario,
            data=email_data.data,
            corpo_email=email_data.corpo_texto if email_data.corpo_texto else
            f'<pre>{email_data.corpo_html}</pre>'
        )

        # Se houver anexos, adiciona a seção de anexos ao HTML.
        if email_data.anexos:
            html_content += """
                    <div class="attachments">
                        <h3>Anexos ({num_anexos})</h3>
                        <ul>
            """.format(num_anexos=len(email_data.anexos))

            # Itera sobre os anexos e adiciona cada um à lista HTML.
            for anexo in email_data.anexos:
                html_content += f"<li>{anexo['filename']} ({anexo['mime_type']})</li>"

            html_content += """
                        </ul>
                    </div>
                """

        # Finaliza a construção da string HTML.
        html_content += """
                </div>
            </body>
            </html>
            """
        return html_content

    def __search_in_gmail_and_save(self, query, limit):
        """
        Busca e-mails na API do Gmail, salva-os no cache e retorna uma lista.

        Args:
            query (str): A string de busca para a API do Gmail.
            limit (int, opcional): O número máximo de e-mails a serem
                                    buscados. O padrão é 50.

        Returns:
            list: Uma lista de objetos Email encontrados.
        """
        # Cria uma lista a partir do gerador de API, limitando o número de itens.
        temp_list = list(itertools.islice(self.__service.geratorAPI(query), limit))

        if temp_list:
            saved = 0
            # Itera sobre a lista de e-mails.
            for email_ in temp_list:
                # Verifica se o ID do e-mail já existe no conjunto.
                if email_.id_ not in self.__emails_ids_set:
                    # Se não, adiciona-o à lista e ao conjunto.
                    self.__emails_list.append(email_)
                    self.__emails_ids_set.add(email_.id_)
                    saved += 1
            # Se novos e-mails foram salvos, a query é adicionada à lista de queries.
            if saved > 0:
                self.__querys_list.append(query)

        return temp_list

    def __search_in_saved_emails(self, query):
        """
        Busca e-mails na lista de cache com base em uma query.

        A busca é feita em vários campos do e-mail (remetente, assunto, corpo).

        Args:
            query (str): A string de busca.

        Returns:
            list: Uma lista de objetos Email que correspondem à busca.
        """
        # Converte a query para minúsculas para uma busca sem distinção de maiúsculas/minúsculas.
        query_lower = query.lower()
        temp_list = []

        # Itera sobre os e-mails salvos.
        for email_ in self.__emails_list:
            # Converte os campos do e-mail para minúsculas.
            remetente = email_.remetente.lower()
            assunto = email_.assunto.lower()
            destinatario = email_.destinatario.lower()
            corpo_texto = email_.corpo_texto.lower()
            corpo_html = email_.corpo_html.lower()

            # Verifica se a query está presente em qualquer um dos campos.
            if (query_lower in remetente or
                    query_lower in assunto or
                    query_lower in destinatario or
                    query_lower in corpo_texto or
                    query_lower in corpo_html):
                temp_list.append(email_)

        # Retorna a lista de e-mails encontrados ou uma lista vazia.
        if temp_list:
            return temp_list
        return []

    def search_emails(self, limit, query='is:unread'):
        """
        Método principal para buscar e-mails.

        Ele decide se a busca deve ser feita localmente (no cache) ou
        remotamente (na API do Gmail).

        Args:
            query (str, opcional): A string de busca. O padrão é is:unread.
            limit (int, opcional): O limite de busca. O padrão é 50

        Returns:
            list: Uma lista de objetos Email encontrados ou None se não
                  houver resultados.
        """
        # Lógica para decidir o tipo de busca.
        # Se a query for 'is:unread', busca diretamente na API.
        if query == 'is:unread':
            temp_list = self.__search_in_gmail_and_save(query, limit)
        # Se a query já foi usada antes, busca no cache.
        elif query in self.__querys_list:
            temp_list = self.__search_in_saved_emails(query)
        # Caso contrário, busca na API e salva no cache.
        else:
            temp_list = self.__search_in_gmail_and_save(query, limit)

        # Se a lista de resultados estiver vazia, imprime uma mensagem e retorna None.
        if not temp_list:
            print('\aNenhum e-mail encontrado')
            return

        return temp_list


class EmailClient:
    """
    Controla a comunicação com a API do Gmail.

    Esta classe lida com a autenticação, envio de e-mails, busca de
    mensagens e processamento de conteúdo.
    """
    __scopes: list[Any]

    __id_usuario: str

    __email_remetente: str

    __id_usuario: str

    def __init__(self, email: Email):
        """
        Inicializa o cliente da API do Gmail.

        Args:
            email_class (class): A classe para criar objetos de e-mail.
        """
        # Define as permissões (scopes) necessárias para a API.
        self.__SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
        self.__id_usuario = id_usuario
        # Chama o método de autenticação para criar o serviço da API.
        self.__service = self.__authenticate()
        # Armazena as classes para uso posterior.
        self.__cache_class = None
        self.__email_class = email
        # Define o endereço de e-mail do remetente.
        self.__email_remetente = 'padagoec@gmail.com'

    def set_cache_clas(self, cache):
        """
        :param cache: Email_Cache
        """
        self.__cache_class = cache

    def __authenticate(self):
        """
        Autentica o usuário com a API do Gmail.

        O método verifica se existe um token de autenticação local. Se
        estiver expirado, tenta renová-lo. Caso contrário, inicia o
        fluxo de autenticação OAuth 2.0.

        Returns:
            build: O objeto de serviço da API do Gmail autenticado.
        """
        credentials = None

        # Verifica se o arquivo de token existe.
        if os.path.exists('token.pickle'):
            # Se existir, carrega as credenciais do arquivo.
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)

        # Se as credenciais não existirem ou forem inválidas.
        if not credentials or not credentials.valid:
            # Se as credenciais existirem, mas estiverem expiradas e com um token de renovação.
            if credentials and credentials.expired and credentials.refresh_token:
                # Renova as credenciais.
                credentials.refresh(Request())

            else:
                # Se não, inicia um novo fluxo de autenticação.
                fluxo = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.__SCOPES
                )
                # Executa o servidor local para o fluxo de autenticação.
                credentials = fluxo.run_local_server(port=0)

            # Salva as novas credenciais em um arquivo.
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)

        # Constrói o serviço da API com as credenciais.
        service = build('gmail', 'v1', credentials=credentials)

        return service

    def send_email(self, body):
        """
        Envia e-mails através da API do Gmail.

        Args:
            body (list): Uma lista de tuplas contendo o corpo da mensagem
                         e o destinatário.
        """
        # Itera sobre a lista de corpos de mensagem.
        for b, des in body:
            try:
                # Envia cada mensagem individualmente.
                self.__service.users().messages().send(userId=self.__id_usuario, body=b).execute()
            except Exception as error:
                # Em caso de erro, imprime uma mensagem.
                print(f'\aError ao enviar: {des} - {error}')

    def write_email(self, to, ass, text, files=None):
        """
        Cria uma mensagem MIME com corpo e anexos.

        Este método constrói a estrutura de um e-mail, adicionando o
        destinatário, remetente, assunto, texto e, opcionalmente,
        anexos.

        Args:
            to (list): Uma lista de e-mails destinatários.
            ass (str): O assunto da mensagem.
            text (str): O corpo do e-mail em texto simples.
            files (list, optional): Uma lista de caminhos para arquivos.
                                    O padrão é None.

        Returns:
            list: Uma lista de mensagens prontas para serem enviadas
                  pela API.
        """
        msgs = []

        # Cria a mensagem MIME de múltiplas partes.
        msg = MIMEMultipart()

        # Define os cabeçalhos da mensagem.
        msg['to'] = ', '.join(to)
        msg['from'] = self.__email_remetente
        msg['subject'] = ass
        # Anexa o corpo do e-mail como texto simples.
        msg.attach(MIMEText(text, 'plain'))

        # Se houver arquivos para anexar.
        if files:
            # Itera sobre cada arquivo.
            for file in files:
                try:
                    # Verifica se o arquivo existe.
                    if not os.path.isfile(file):
                        print(f'Arquivo não encontrado: {file}')
                        continue

                    # Adivinha o tipo MIME e a codificação do arquivo.
                    type_arch, encoding = mimetypes.guess_type(file)

                    # Se o tipo não for reconhecido, define como um tipo genérico.
                    if type_arch is None or encoding is not None:
                        type_arch = 'application/octet-stream'

                    # Separa o tipo e o subtipo do MIME.
                    type_, sub_type = type_arch.split('/', 1)

                    mime_ = None
                    # Abre o arquivo em modo binário.
                    with open(file, 'rb') as f:
                        # Cria o objeto MIME com base no tipo de arquivo.
                        if type_ == 'text':
                            mime_ = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)
                        elif type_ == 'image':
                            mime_ = MIMEImage(f.read(), _subtype=sub_type)
                        else:
                            mime_ = MIMEBase(type_, sub_type)
                            mime_.set_payload(f.read())

                        # Codifica o conteúdo em base64.
                        email.encoders.encode_base64(mime_)

                    # Obtém o nome do arquivo a partir do caminho.
                    name = os.path.basename(file)

                    # Adiciona o cabeçalho 'Content-Disposition' para definir o anexo.
                    mime_.add_header('Content-Disposition', 'attachment', filename=name)

                    # Anexa o arquivo à mensagem.
                    msg.attach(mime_)

                except Exception as error:
                    # Em caso de erro ao anexar, imprime uma mensagem.
                    print(f'\aError ao anexar arquivo: {error}')

        # Codifica a mensagem completa (cabeçalhos e corpo) em Base64 URL-safe.
        encoded_message_bytes = base64.urlsafe_b64encode(msg.as_bytes())
        raw_message = encoded_message_bytes.decode('utf-8')

        # Adiciona a mensagem bruta e a lista completa de destinatários à lista.
        msgs.append(({'raw': raw_message}, ', '.join(to)))

        return msgs

    def __gerator_emails(self, query):
        """
        Um gerador que busca e-mails na API do Gmail em lotes.

        Este método otimiza o uso de memória ao buscar e-mails em pequenas
        partes, usando tokens de paginação para continuar a busca.

        Args:
            query (str): A string de busca para a API.

        Yields:
            dict: Um dicionário de mensagem bruta da API.
        """
        try:
            # Faz a primeira chamada à API para a lista de mensagens.
            resposta = self.__service.users().messages().list(userId=self.__id_usuario, q=query).execute()

            # Se houver mensagens na resposta, retorna cada uma como um gerador.
            if 'messages' in resposta:
                for messages in resposta['messages']:
                    yield messages

            # Continua buscando até que não haja mais páginas de resultados.
            while 'nextPageToken' in resposta:
                page_token = resposta['nextPageToken']
                # Faz a próxima chamada à API com o token de paginação.
                resposta = self.__service.users().messages().list(userId=self.__id_usuario, q=query,
                                                                  pageToken=page_token).execute()
                # Retorna as mensagens da nova página.
                if 'messages' in resposta:
                    for messages in resposta['messages']:
                        yield messages

        except Exception as error:
            # Em caso de erro na geração, imprime uma mensagem.
            print(f'Erro ao gerar mensagens: {error}')

    def geratorAPI(self, query):
        """
        Processa mensagens brutas da API e retorna objetos Email.

        Args:
            query (str): A string de busca para a API.

        Yields:
            Email: Um objeto Email preenchido com os dados da mensagem.
        """
        # Itera sobre as mensagens do gerador.
        for msg in self.__gerator_emails(query):
            # Obtém o conteúdo completo da mensagem.
            msg_content = self.__get_content(msg['id'])

            # Se o conteúdo não for obtido, pula para o próximo.
            if not msg_content:
                print(f'\aErro ao obter mensagem - ID {msg['id']}')
                continue

            # Dicionário para armazenar os dados do e-mail.
            email_data = {
                'id': msg['id'], 'assunto': '', 'remetente': '', 'destinatario': '',
                'data': '', 'corpo_texto': '', 'corpo_html': '', 'anexos': []
            }

            # Se houver um payload (conteúdo) na mensagem.
            if 'payload' in msg_content:
                payload = msg_content['payload']

                # Extrai os cabeçalhos.
                if 'headers' in payload:
                    for cabecalho in payload['headers']:
                        name = cabecalho['name'].lower()
                        # Popula o dicionário com os dados dos cabeçalhos.
                        if name == 'subject':
                            email_data['assunto'] = cabecalho['value']
                        elif name == 'from':
                            email_data['remetente'] = cabecalho['value']
                        elif name == 'to':
                            email_data['destinatario'] = cabecalho['value']
                        elif name == 'date':
                            email_data['data'] = cabecalho['value']

                # Extrai as partes do corpo da mensagem.
                if 'parts' in payload:
                    self.__get_parts(payload.get('parts'), email_data)

            # Cria um novo objeto Email com os dados extraídos.
            new_email = Email(email_data)
            # Retorna o objeto como um gerador.
            yield new_email

    def __get_content(self, id_msg):
        """
        Busca o conteúdo completo de uma mensagem na API do Gmail.

        Args:
            id_msg (str): O ID da mensagem.

        Returns:
            dict: O objeto de mensagem completo da API, ou None em caso de erro.
        """
        try:
            # Usa o serviço da API do Gmail para obter a mensagem com formato 'full'.
            mensagem = self.__service.users().messages().get(userId=self.__id_usuario, id=id_msg,
                                                             format='full').execute()
            return mensagem
        except Exception as error:
            print(f'\aError ao obter a mensagem: {error}')
            return None

    def __get_parts(self, parts, email_data):
        """
        Analisa as partes de uma mensagem MIME e extrai dados relevantes.

        Este método percorre recursivamente as partes do e-mail para encontrar
        o corpo do texto (HTML ou texto simples) e os anexos.

        Args:
            parts (list): A lista de partes da mensagem.
            email_data (dict): O dicionário onde os dados extraídos serão salvos.
        """
        # Se não houver partes, retorna.
        if not parts:
            return

        for part in parts:
            mime_type = part.get('mimeType')
            data = part['body'].get('data')

            # Se a parte for multipart, chama a função recursivamente.
            if 'multipart' in mime_type:
                self.__get_parts(part.get('parts'), email_data)
            # Se for HTML, decodifica e salva.
            elif mime_type == 'text/html' and data:
                email_data['corpo_html'] = self.__decode_base64(data)
            # Se for texto, salva se o corpo HTML ainda não foi preenchido.
            elif mime_type == 'text/plain' and data:
                if not email_data['corpo_html']:
                    email_data['corpo_html'] = self.__decode_base64(data)
            # Se a parte for um anexo, extrai os dados do anexo e o adiciona à lista.
            elif 'attachment' in part.get('filename', '').lower():
                file_data = {
                    'filename': part.get('filename'),
                    'mime_type': mime_type,
                    'data': part['body'].get('data')
                }
                email_data['anexos'].append(file_data)

    def __decode_base64(self, data):
        """
        Decodifica uma string de dados base64-urlsafe para UTF-8.

        Args:
            data (str): A string a ser decodificada.

        Returns:
            str: A string decodificada, ou uma string vazia se os dados
                 forem nulos.
        """
        # Verifica se os dados existem antes de tentar decodificar.
        if not data:
            return ''

        # Decodifica a string usando base64url e UTF-8.
        return base64.urlsafe_b64decode(data).decode('utf-8')
