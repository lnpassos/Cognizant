import openai


class Chatbot:
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.messages = []
        self.predefined_questions = [
            (
                "O que é esse projeto?",
                "Este projeto é um sistema de controle de URLs, ou como eu gosto de chamar: 'Pastas', para envio e gerenciamento de arquivos. Você pode salvar e acessar seus arquivos a qualquer momento.",
            ),
            (
                "Como usar o projeto?",
                "Para utilizar o sistema, siga os seguintes passos:<br><br>"
                "1️⃣ <b>**Autenticação**</b>: Crie uma conta e faça login para acessar o sistema.<br><br>"
                "2️⃣ <b>**Acesso ao sistema**</b>: Após fazer login, você será direcionado à página inicial, onde pode criar sua primeira pasta.<br><br>"
                "3️⃣ <b>**Criação de URL**</b>: Clique em 'Insert a URL', escolha um nome para sua URL, como 'documents/reviews'. Você pode, opcionalmente, enviar um arquivo junto, clicando no ícone de nuvem. Em seguida, clique em 'Send'.<br><br>"
                "4️⃣ <b>**Acesso aos arquivos**</b>: Após criar sua URL, ela aparecerá na aba de pastas. Clique na pasta correspondente para visualizar os arquivos.<br><br>"
                "5️⃣ <b>**Gerenciamento de arquivos**</b>:<br>"
                "   - 📂 <b>**Visualização**</b>: Veja todos os arquivos enviados dentro da pasta correspondente.<br>"
                "   - 🔍 <b>**Filtro**</b>: Utilize a barra de pesquisa para encontrar arquivos facilmente.<br>"
                "   - ❌ <b>**Exclusão**</b>: Caso necessário, exclua arquivos indesejados.<br>"
                "   - 👁️ <b>**Visualização**</b>: Clique no ícone de olho para visualizar arquivos compatíveis. Se o arquivo não puder ser lido diretamente, ele não será exibido.<br><br>"
                "💡 <b>**Dica**</b>: Você pode enviar arquivos diretamente pelo input de URL, sem precisar estar dentro da pasta. Basta repetir a URL e enviar um novo arquivo.<br><br>"
                "📌 <b>**Recursos disponíveis**</b>:<br>"
                "- Criar URLs e enviar arquivos simultaneamente.<br>"
                "- Acessar pastas associadas às URLs criadas.<br>"
                "- Visualizar, deletar e gerenciar versões dos arquivos enviados.<br>"
                "- Filtrar arquivos e URLs facilmente.<br>"
                "- Criar novos arquivos diretamente na pasta correspondente.<br><br>"
                "Espero que tenha ficado tudo bem claro! Caso tenha dúvidas, <b>consulte este guia novamente</b>! 🚀",
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
            return "👋 Olá, sou o <b>Leo</b> e hoje eu serei o seu <b>guia</b>! Vamos começar?<br><br>Digite <b>'1'</b> para CONTINUAR ou <b>'2'</b> para SAIR<br><br>"
        else:
            return self.process_user_choice(message)

    def continue_help(self):
        """Envia o guia completo após o usuário escolher continuar"""
        help_text = ""
        # Adicionando as perguntas e respostas do guia
        for question, answer in self.predefined_questions:
            help_text += f"❓ {question}<br>💬 Leo: {answer}<br><br>"
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
            return "Escolha inválida. Digite '1' para continuar ou '2' para sair."
