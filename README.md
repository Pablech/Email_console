# Email_console

Gerenciador de E-mail via Linha de Comando

Este é um aplicativo de linha de comando para interagir com sua conta do Gmail de forma segura e eficiente. Ele permite que você envie e-mails, pesquise na sua caixa de entrada, e gerencie contatos e credenciais de forma local, usando uma interface de terminal intuitiva.

Funcionalidades

    Envio de E-mails: Com suporte a múltiplos destinatários, assunto, corpo da mensagem e anexos.

    Busca e Paginação: Pesquise e-mails na sua caixa de entrada do Gmail. A busca é otimizada com um sistema de cache local para evitar chamadas repetidas à API.

    Visualização de E-mails: Abra e-mails diretamente no seu navegador padrão para uma visualização completa, incluindo o conteúdo HTML.

    Segurança de Login: Suas senhas são armazenadas com segurança usando o algoritmo de hash bcrypt.

    Autocompletar Inteligente: Use a tecla TAB para autocompletar comandos e contatos, melhorando a produtividade.

    Armazenamento Local: Contatos e credenciais de login são salvos em um banco de dados MySQL para acesso rápido.

Requisitos

Para rodar este projeto, você precisará ter:

    Python 3.x

    MySQL Server ou MariaDB

    Acesso à API do Gmail: Siga os passos abaixo para configurar suas credenciais.

Instalação

Siga estes passos para configurar e rodar o projeto:

1. Clone o repositório:
    Bash
    
    git clone https://github.com/Pablech/Email_console

2. Accese ao diretório:
   Bash
   
   cd Email_console

3. Configure a API do Gmail:
Para usar a API do Gmail, você precisa obter um arquivo credentials.json.

    Vá para o Console de [Desenvolvedores do Google](https://console.cloud.google.com/).

    Crie um novo projeto.

    Vá em "Biblioteca" e ative a "API do Gmail".

    Vá em "Credenciais", clique em "Criar Credenciais" e selecione "ID do cliente OAuth".

    Configure a Tela de Consentimento OAuth.

    Crie um "ID do cliente OAuth" do tipo "Aplicativo para computador".

    Baixe o arquivo JSON e renomeie-o para credentials.json. Coloque-o no mesmo diretório dos seus arquivos de código.

4. Crie um ambiente virtual:
   Bash

   python -m venv .venv ou python3 -m venv .venv

5. Ative o ambiente virtual:
   Bash

   source .venv/bin/activate

6. Instale as dependências do Python:
   Bash

   pip install -r requirements.txt

7. Inicie o programa:
   Bash

   python main.py
   ou
   python3 main.py

   Na primeira execução, o aplicativo pedirá a senha do seu usuário root do MySQL para se conectar e criar o banco de dados e as tabelas necessárias automaticamente (DESENVOLVIDO E TESTADO COM MariaDB). Em seguida, iniciará o processo de autenticação com a API do Google. Uma janela do navegador será aberta para que você autorize o acesso à sua conta do Gmail.

Como Usar

O aplicativo funciona através de comandos de linha. Use a tecla TAB para autocompletar.

    send= <email1> <email2> ...: Envia um novo e-mail.

        ass= <assunto>: Adiciona um assunto (opcional).

        msg= <mensagem>: Adiciona o corpo da mensagem (opcional).

        file= <caminho_do_arquivo1> <caminho_do_arquivo2> ...: Anexa arquivos (opcional).

    Exemplo:

    main@[main]~ send= contato@exemplo.com ass= Reuniao msg= Ola, vamos nos reunir as 10h. file= anexo.pdf

    search= <query>: Busca e-mails com base em uma query.

        limit= <número>: Limita o número de resultados (opcional, padrão 50).

        Exemplo:

    main@[main]~ search= from:pedro is:unread limit= 10

    show= <número>: Abre um e-mail específico. O número corresponde à posição na lista exibida.

    next= / prev=: Navega entre as páginas de resultados da busca.

    help=: Exibe uma lista de todos os comandos disponíveis.

    quik=: Encerra o programa de forma segura a qualquer momento.

## Contribuição

Sinta-se à vontade para abrir issues ou enviar pull requests com melhorias ou correções!

## Licença

Este projeto está sob a licença MIT.

---

Desenvolvido por [Pablech](https://github.com/Pablech)
E-mail [Pablech](pablech@proton.me)

