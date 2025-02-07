import { useState } from "react";
import styles from "../styles/components/ChatBot.module.css";

const ChatBot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [chatMode, setChatMode] = useState(null);
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    const handleChatModeChange = (mode) => {
        setChatMode(mode);

        if (messages.length === 0) {
            setMessages([{ role: "assistant", content: `You are in ${mode} mode. Type anything to continue! 🚀` }]);
        }
    };

    const resetChat = () => {
        setMessages([]);
        setChatMode(null); 
    };

    const sendMessage = async (message) => {
        if (!message.trim()) return;

        if (message.trim() === "2") {
            const newMessages = [...messages, { role: "assistant", content: "👋 See you later! Returning to the main menu..." }];
            setMessages(newMessages);
            setIsLoading(true);
            
            setTimeout(() => {
                resetChat();  
                setIsLoading(false); 
            }, 3000); 

            return;
        }

        const newMessages = [...messages, { role: "user", content: message }];
        setMessages(newMessages);
        setInput("");
        setIsLoading(true);

        const response = await fetch("/api/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, chatMode }),
        });

        const data = await response.json();
        setMessages([...newMessages, { role: "assistant", content: data.reply }]);
        setIsLoading(false);
    };

    return (
        <div className={styles.chatContainer}>
            {!isChatOpen ? (
                <button className={styles.chatButton} onClick={() => setIsChatOpen(true)}>
                    🤖 Virtual Assistant
                </button>
            ) : (
                <div className={styles.chatBox}>
                    <div className={styles.chatHeader}>
                        <h3>🤖 Virtual Assistant</h3>
                        <button onClick={() => setIsChatOpen(false)}>✖</button>
                    </div>
                    {!chatMode ? (
                        <div className={styles.chatOptions}>
                            <button onClick={() => handleChatModeChange("help")}>❓ Need Help</button>
                            <button onClick={() => handleChatModeChange("free")}>🗨️ Free Conversation</button>
                        </div>
                    ) : (
                        <>
                            <div className={styles.chatMessages}>
                                {messages.map((msg, index) => (
                                    <div
                                        key={index}
                                        className={msg.role === "user" ? styles.userMessage : styles.botMessage}
                                        dangerouslySetInnerHTML={{ __html: msg.content }}
                                    />
                                ))}
                                {isLoading && <div className={styles.loading}>⏳ Waiting for response...</div>}
                            </div>

                            <div className={styles.chatInput}>
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Type your message..."
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
