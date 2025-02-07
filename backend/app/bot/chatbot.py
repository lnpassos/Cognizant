import openai

""" 
Hi there! 👋
how are you doing? 

I implemented this Chatbot as a guide to help you navigate the system in a dynamic way, 
knowing what functions are available and being able to test them one by one, making your life easier!. 

Of course, we could build something much more robust by leveraging machine learning with tools 
like Pytorch or scikit-learn and data science techniques to analyze user behavior and deliver a faster, more dynamic experience.

AI could also be used to develop new features based on user needs, gathering insights and adapting the system intelligently to enhance usability and efficiency.

This is just a starting point, and there are many possibilities to explore in the future :)

Thanks!
~ Leo

"""


class Chatbot:
    def __init__(self, api_key, model="gpt-3.5-turbo"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.messages = []
        self.predefined_questions = [
            (
                "<b>What is this project?</b><br>",
                " This project is a <b>URL control system</b>, or as I like to call it: <b>Folders</b>. <br><br>Created with a focus on <b>file management</b>, where you can <b>save</b> and <b>access</b> them at any time.",
            ),
            (
                "<b>How to use the project?</b><br>",
                " To use the system, follow these steps:<br><br>"
                "1️⃣ <b>** Authentication **</b><br>Create an account and log in to access the system.<br><br>To make your experience <b>faster</b> and <b>more dynamic</b>, the only validation we have is for <b>Email</b>. Consider using something like <b>yourname@gmail.com</b> as an example.<br><br>"
                "2️⃣ <b>** System Access **</b><br> After logging in, you will be directed to <b>Home</b>, where you can create and manage your folders.<br><br>"
                "3️⃣ <b>** URL Creation **</b><br> Click on 'Insert a URL' and choose a name for your URL, such as: <b>'documents/reviews'</b>.<br><br> You can also optionally upload one or more files together by clicking on the <b>Cloud</b> icon. Finally, click on <b>'Send'</b>.<br><br>"
                "4️⃣ <b>** Accessing Files **</b><br> After creating your URL, it will appear in the folders tab. <br><br>Click on the desired folder to <b>view the files.</b><br><br>"
                "5️⃣ <b>** File Management **</b><br>"
                " Here you can view and manage all your files uploaded via the desired URL.<br><br>"
                "   📂 <b>** Viewing **</b><br> See all files uploaded within the corresponding folder.<br><br>"
                "   🔍 <b>** Filter **</b><br> Use the search bar to easily find folders or files. (On their respective pages)<br><br>"
                "   ❌ <b>** Deletion **</b><br> If necessary, delete unwanted folders or files by clicking on the <b>X</b>.<br><br>"
                "   👁️ <b>** Viewing **</b><br> Click on the eye icon to view files compatible with the browser.<br><br> If the file cannot be read directly, it will not be displayed.<br><br>"
                "   📥 <b>** Download **</b><br> Click on the download icon to download the desired file.<br><br>"
                "💡 <b>** Tip **</b><br> You can send files directly through the direct URL input on the Home page without needing to be inside the folder. Just repeat the URL and send a new file.<br><br>"
                "📌 <b>** Available Features **</b>:<br>"
                "● Create URLs and upload files simultaneously.<br><br>"
                "● Upload one or more files to an existing URL by simply re-entering the URL in the input.<br><br>"
                "● Access folders associated with created URLs.<br><br>"
                "● View, delete, and manage versions of uploaded files.<br><br>"
                "● Easily filter files and URLs.<br><br>"
                "● Upload new files directly to the desired folder.<br><br>"
                "I hope everything is clear! If you have any questions, feel free to <b>consult this guide again</b>! 🚀",
            ),
        ]

    def send_message(self, message):
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
            return f"Error communicating with the API: {str(e)}"

    # Linear help mode
    def help_mode(self, message=None):
        if message is None:
            return "👋 Hello, I am <b>Leo</b>, and today I will be your <b>guide</b>! Shall we begin?<br><br>Type <b>1</b> to <b>CONTINUE</b> or <b>2</b> to <b>EXIT</b><br><br>"
        else:
            return self.process_user_choice(message)

    def continue_help(self):
        help_text = ""
        for question, answer in self.predefined_questions:
            help_text += f"❓ {question}<br>💬{answer}<br><br>"
        help_text += "<br>If you want to return to the main menu, type <b>'2'</b>.<br>"
        return help_text

    # Free chat mode with ChatGPT AI
    def free_chat_mode(self, message):
        if message.strip() == "2":
            return self.end_help()
        else:
            self.messages.append({"role": "user", "content": message})
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )
            assistant_message = response.choices[0].message
            self.messages.append(
                {"role": "assistant", "content": assistant_message.content}
            )
            return f"{assistant_message.content}<br><br>Type <b>'2'</b> to EXIT."

    # Continue or exit help mode
    def process_user_choice(self, user_choice):
        if user_choice == "1":
            return self.continue_help()
        elif user_choice == "2":
            return self.end_help()
        else:
            return "Invalid choice. Type <b>1</b> to <b>continue</b> or <b>2</b> to <b>exit</b>."
