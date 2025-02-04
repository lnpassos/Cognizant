export default async function handler(req, res) {
    if (req.method !== "POST") {
        return res.status(405).json({ message: "Método não permitido" });
    }

    const { message, chatMode } = req.body;

    try {
        const response = await fetch("http://localhost:8000/chatbot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, chatMode }),
        });

        const data = await response.json();
        res.status(200).json({ reply: data.reply });
    } catch (error) {
        res.status(500).json({ reply: "Erro ao conectar com o chatbot." });
    }
}
