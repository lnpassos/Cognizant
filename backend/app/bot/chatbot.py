import openai


class Chatbot:
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.messages = []
        self.predefined_questions = [
            (
                "<b>O que é esse projeto?</b><br>",
                " Este projeto é um <b>sistema de controle de URL's</b>, ou como eu gosto de chamar: <b>Pastas</b>. <br><br>Criado com foco em <b>gerenciamento de arquivos</b>, nos quais você pode <b>salva-los</b> e <b>acessa-los</b> a qualquer momento.",
            ),
            (
                "<b>Como usar o projeto?</b><br>",
                " Para utilizar o sistema, siga os seguintes passos:<br><br>"
                "1️⃣ <b>** Autenticação **</b><br>Crie uma conta e faça login para acessar o sistema.<br><br>Para tornar a sua experiência mais <b>rápida</b> e <b>dinâmica</b>, a única validação que temos é para <b>E-mail</b>. Cogite usar algo como <b>seunome@gmail.com</b> por exemplo.<br><br>"
                "2️⃣ <b>** Acesso ao sistema **</b><br> Após fazer login, você será direcionado à <b>Home</b>, onde pode criar e gerenciar suas pastas.<br><br>"
                "3️⃣ <b>** Criação de URL **</b><br> Clique em 'Insert a URL' e escolha um nome para sua URL, como por exemplo: <b>'documents/reviews'</b>.<br><br> Você também pode, opcionalmente, enviar um ou mais arquivos juntos, clicando no ícone de <b>Nuvem</b>. Por fim, clique em <b>'Send'</b>.<br><br>"
                "4️⃣ <b>** Acesso aos arquivos **</b> Após criar sua URL, ela aparecerá na aba de pastas. <br><br>Clique na pasta desejada para <b>visualizar os arquivos.</b><br><br>"
                "5️⃣ <b>** Gerenciamento de arquivos **</b><br>"
                " Aqui você pode visualizar e gerenciar todos seus arquivos enviados pela URL desejada.<br><br>"
                "   📂 <b>** Visualização **</b><br> Veja todos os arquivos enviados dentro da pasta correspondente.<br><br>"
                "   🔍 <b>** Filtro **</b><br> Utilize a barra de pesquisa para encontrar pastas ou arquivos facilmente. (Em suas respectivas páginas)<br><br>"
                "   ❌ <b>** Exclusão **</b><br> Caso necessário, exclua pastas ou arquivos indesejados clicando no <b>X</b>.<br><br>"
                "   👁️ <b>** Visualização **</b><br> Clique no ícone de olho para visualizar arquivos compatíveis com o navegador.<br><br> Se o arquivo não puder ser lido diretamente, ele não será exibido.<br><br>"
                "   📥 <b>** Download **</b><br> Clique no ícone de download para baixar o arquivo que desejar.<br><br>"
                "💡 <b>** Dica **</b><br> Você pode enviar arquivos diretamente pelo input de URL direto pela Home, sem precisar estar dentro da pasta. Basta repetir a URL e enviar um novo arquivo.<br><br>"
                "📌 <b>** Recursos disponíveis **</b>:<br>"
                "● Criar URLs e/ou enviar arquivos simultaneamente.<br><br>"
                "● Enviar um ou mais arquivos para uma URL existente, apenas passandoa URL no input novamente.<br><br>"
                "● Acessar pastas associadas às URLs criadas.<br><br>"
                "● Visualizar, deletar e gerenciar versões dos arquivos enviados.<br><br>"
                "● Filtrar arquivos e URLs facilmente.<br><br>"
                "● Enviar novos arquivos diretamente na pasta que desejar.<br><br>"
                "Espero que tenha ficado tudo bem claro! Caso tenha ficado alguma dúvida, fique à vontade para <b>consultar este guia novamente</b>! 🚀",
            ),
        ]

    def send_message(self, message):
        """Envio de mensagem para o ChatGPT e retorno da resposta"""
        try:
            self.messages.append({"role": "user", "content": message})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )
            assistant_message = response.choices[0].message
            self.messages.append(
                {"role": "assistant", "content": assistant_message.content}
            )
            return assistant_message.content
        except Exception as e:
            return f"Erro ao se comunicar com a API: {str(e)}"

    def help_mode(self, message=None):
        """Modo de ajuda linear, onde o usuário recebe uma pergunta de cada vez."""
        if message is None:
            # Boas-vindas e opções para continuar ou sair
            return "👋 Olá, sou o <b>Leo</b> e hoje eu serei o seu <b>guia</b>! Vamos começar?<br><br>Digite <b>1</b> para <b>CONTINUAR</b> ou <b>2</b> para <b>SAIR</b><br><br>"
        else:
            return self.process_user_choice(message)

    def continue_help(self):
        """Envia o guia completo após o usuário escolher continuar"""
        help_text = ""
        # Adicionando as perguntas e respostas do guia
        for question, answer in self.predefined_questions:
            help_text += f"❓ {question}<br>💬{answer}<br><br>"
        # Mensagem de finalização com opção de voltar ao menu inicial
        help_text += "<br>Caso queira voltar ao menu inicial, digite <b>'2'</b>.<br>"
        return help_text

    def end_help(self):
        """Mensagem de despedida ou fim de interação"""
        return "👋 Até logo! Se precisar de ajuda, estarei por aqui! 😊"

    def free_chat_mode(self, message):
        """Modo de conversa livre com opção de sair."""
        if message.strip() == "2":
            return self.end_help()  # Retorna a mensagem de despedida
        else:
            # Adiciona a mensagem do usuário ao histórico
            self.messages.append({"role": "user", "content": message})
            # Gera a resposta do chatbot
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )
            assistant_message = response.choices[0].message
            self.messages.append(
                {"role": "assistant", "content": assistant_message.content}
            )
            # Adiciona a opção de sair após a resposta
            return f"{assistant_message.content}<br><br>Digite <b>'2'</b> para SAIR."

    def process_user_choice(self, user_choice):
        """Processa a escolha do usuário entre '1' (continuar) ou '2' (sair)."""
        if user_choice == "1":
            return self.continue_help()
        elif user_choice == "2":
            return self.end_help()
        else:
            return "Escolha inválida. Digite <b>1</b> para <b>continuar</b> ou <b>2</b> para <b>sair</b>."
