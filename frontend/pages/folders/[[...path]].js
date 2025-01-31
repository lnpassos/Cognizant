import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import { uploadFile, downloadFile, deleteFile } from "../api/folder"; // Função de deleteFile adicionada

function FolderPage() {
  const router = useRouter();
  const { path } = router.query; // 'path' contém a estrutura da pasta (ex: ['documents', 'reviews'])
  const folderPath = Array.isArray(path) ? path.join("/") : "";
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (folderPath) {
      fetchFiles();
    }
  }, [folderPath]);

  // Função para buscar os arquivos da pasta
  const fetchFiles = async () => {
    if (!folderPath) return;

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/folders/${encodeURIComponent(folderPath)}/files/`,
        {
          method: "GET",
          credentials: "include", // Inclui o cookie com o token
        }
      );

      if (response.status === 401) {
        // Se a resposta for 401 (token não encontrado), redireciona para o login
        router.push("/session-expired");  // Redireciona para a página "Sessão Expirada"
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setFiles(data || []);
      }
    } catch (error) {
      console.error("Erro ao buscar arquivos:", error);
    } finally {
      setLoading(false);
    }
  };

  // Função para fazer o upload do arquivo
  const handleFileUpload = async (event) => {
    const files = event.target.files; // Pega todos os arquivos selecionados
    if (!files.length || !folderPath) return;
  
    try {
      const uploadPromises = Array.from(files).map(async (file) => {
        return uploadFile(folderPath, file); // Faz upload de cada arquivo individualmente
      });
  
      await Promise.all(uploadPromises); // Espera todos os uploads terminarem
  
      await fetchFiles(); // Atualiza a lista de arquivos após o upload
    } catch (error) {
      console.error("Erro no upload:", error);
    }
  
    // Reseta o input para permitir selecionar os mesmos arquivos novamente
    event.target.value = "";
  };

  // Função para fazer o download do arquivo
  const handleFileDownload = (fileName) => {
    if (!folderPath) return;
    downloadFile(folderPath, fileName);
  };

  // Função para deletar o arquivo
  const handleFileDelete = async (fileName) => {
    if (!folderPath || !fileName) return;
  
    try {
      // Formata a URL corretamente
      const response = await fetch(
        `http://localhost:8000/delete_file/${encodeURIComponent(folderPath)}/${encodeURIComponent(fileName)}`,
        {
          method: "DELETE",
          credentials: "include", // Inclui o cookie com o token
        }
      );
  
      if (response.ok) {
        fetchFiles(); // Atualiza a lista de arquivos após a exclusão
      } else {
        const errorData = await response.json();
        alert(errorData.detail || "Erro ao deletar arquivo");
      }
    } catch (error) {
      console.error("Erro ao deletar arquivo:", error);
    }
  };
  

  return (
    <div>
      <h1>Pasta: {folderPath || "Carregando..."}</h1>

      <input
        type="file"
        ref={fileInputRef}
        style={{ display: "none" }}
        multiple
        onChange={handleFileUpload}
      />
      <button onClick={() => fileInputRef.current.click()}>📤 Fazer Upload</button>

      {loading ? (
        <p>Carregando arquivos...</p>
      ) : files.length > 0 ? (
        <ul>
          {files.map((file, index) => (
            <li key={index}>
              {file.filename}
              <button onClick={() => handleFileDownload(file.filename)}>
                Baixar
              </button>
              <button onClick={() => handleFileDelete(file.filename)} style={{ marginLeft: '10px' }}>
                Deletar
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p>Nenhum arquivo encontrado.</p>
      )}
    </div>
  );
}

export default FolderPage;
