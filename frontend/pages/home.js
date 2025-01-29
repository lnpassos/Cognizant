import { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);

  useEffect(() => {
    // Buscar informações do usuário
    axios
      .get("http://localhost:8000/home/", { withCredentials: true })
      .then((response) => {
        setUsername(response.data.message);
      })
      .catch(() => {
        setError("Sessão expirada. Faça login novamente.");
        setTimeout(() => (window.location.href = "/"), 2000); 
      });
  
    // Buscar arquivos do usuário
    axios
      .get("http://localhost:8000/files/", { withCredentials: true })
      .then((response) => {
        setFiles(response.data);
      })
      .catch(() => {
        console.error("Não foi possível carregar os arquivos."); // Agora só loga o erro
      });
  }, []);
  

  const handleLogout = () => {
    axios
      .post("http://localhost:8000/logout/", {}, { withCredentials: true })
      .then(() => {
        window.location.href = "/"; // Redireciona para login
      });
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert("Por favor, selecione um arquivo.");
      return;
    }
  
    setError(""); // Limpa mensagens de erro antigas
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      // Fazendo o upload do arquivo
      const uploadResponse = await axios.post("http://localhost:8000/upload/", formData, {
        withCredentials: true,
        headers: { "Content-Type": "multipart/form-data" },
      });
  
      // Logando a resposta do upload
      console.log("Upload Response:", uploadResponse.data);
  
      setFile(null);
  
      // Atualiza automaticamente a lista de arquivos
      fetchFiles(); 
  
    } catch (error) {
      console.error("Upload Error:", error.response ? error.response.data : error);
    }
  };
  
  const fetchFiles = async () => {
    try {
      const response = await axios.get("http://localhost:8000/files/", { withCredentials: true });
  
      // Verificar se os arquivos foram retornados
      console.log("Arquivos retornados:", response.data);
  
      if (response.data && Array.isArray(response.data)) {
        setFiles(response.data); // Atualiza os arquivos
      } 
    } 
      catch (error) {
      console.error("Erro ao listar arquivos:", error);
      setError("Erro ao carregar arquivos.");
    }
  };
  

  const handleDownload = (filename) => {
    
    const downloadUrl = `http://localhost:8000/download/${encodeURIComponent(filename)}`;
    
    axios
      .get(downloadUrl, { responseType: "blob" })
      .then((response) => {
        console.log("Download realizado com sucesso:", filename); // Debug
  
        const fileURL = URL.createObjectURL(response.data);
        const link = document.createElement("a");
        link.href = fileURL;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch((error) => {
        console.error("Erro ao fazer download do arquivo:", error); // Debug
        setError("Erro ao fazer download do arquivo.");
      });
  };


  return (
    <div>
      {error ? (
        <h1>{error}</h1>
      ) : (
        <>
          <h1>{username}</h1>
          <button onClick={handleLogout}>Logout</button>

          <h2>Upload de Arquivo</h2>
          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            accept="*/*" // Aceita todos os tipos de arquivo
          />
          <button onClick={handleFileUpload}>Upload</button>

          <h2>Arquivos Enviados</h2>
          {files.length === 0 ? (
            <p>Nenhum arquivo enviado ainda.</p>
          ) : (
            <ul>
              {files.map((file, index) => (
                <li key={index}>
                  {file.filename}{" "}
                  <button onClick={() => handleDownload(file.filename)}>Download</button>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
