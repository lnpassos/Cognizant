import { useState } from "react";
import styles from "../styles/components/ChatBot.module.css";

const ChatBot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [chatMode, setChatMode] = useState(null); // null = sem escolha, "free" = conversa livre, "help" = ajuda
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false); // Novo estado para controlar o carregamento

    const handleChatModeChange = (mode) => {
        setChatMode(mode);

        // Adiciona uma mensagem de introdução para o novo modo
        if (messages.length === 0) {
            setMessages([{ role: "assistant", content: `Você está no modo de ${mode}. Digite qualquer coisa para continuarmos! 🚀` }]);
        }
    };

    const sendMessage = async (message) => {
        if (!message.trim()) return;
    
        const newMessages = [...messages, { role: "user", content: message }];
        setMessages(newMessages);
        setInput("");
        setIsLoading(true);
    
        const response = await fetch("/api/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, chatMode }), // Passando chatMode no corpo
        });
    
        const data = await response.json();
        setMessages([...newMessages, { role: "assistant", content: data.reply }]);
        setIsLoading(false);
    
        // Verifica se a resposta é a mensagem de despedida
        if (data.reply.includes("👋 Até logo!")) {
            setChatMode(null);
            setMessages([]);
        }
    };

    return (
        <div className={styles.chatContainer}>
            {!isChatOpen ? (
                <button className={styles.chatButton} onClick={() => setIsChatOpen(true)}>
                    🤖 Assistente Virtual
                </button>
            ) : (
                <div className={styles.chatBox}>
                    <div className={styles.chatHeader}>
                        <h3>🤖 Assistente Virtual</h3>
                        <button onClick={() => setIsChatOpen(false)}>✖</button>
                    </div>
                    {!chatMode ? (
                        <div className={styles.chatOptions}>
                            <button onClick={() => handleChatModeChange("help")}>❓ Preciso de Ajuda</button>
                            <button onClick={() => handleChatModeChange("free")}>🗨️ Conversa Livre</button>
                        </div>
                    ) : (
                        <>
                            <div className={styles.chatMessages}>
                                {messages.map((msg, index) => (
                                    <div
                                        key={index}
                                        className={msg.role === "user" ? styles.userMessage : styles.botMessage}
                                        // Usando dangerouslySetInnerHTML para interpretar HTML nas mensagens
                                        dangerouslySetInnerHTML={{ __html: msg.content }}
                                    />
                                ))}
                                {isLoading && <div className={styles.loading}>⏳ Aguardando resposta...</div>} {/* Exibe uma mensagem de loading */}
                            </div>

                            <div className={styles.chatInput}>
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Digite sua mensagem..."
                                    onKeyPress={(e) => e.key === "Enter" && sendMessage(input)}
                                />
                                <button onClick={() => sendMessage(input)}>➤</button>
                            </div>
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default ChatBot;
