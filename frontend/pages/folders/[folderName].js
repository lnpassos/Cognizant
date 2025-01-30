import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import { uploadFile, downloadFile } from "../api/folder"; // Funções de upload e download

function FolderPage() {
  const router = useRouter();
  const { folderName } = router.query;
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);

  // Fetch dos arquivos ao carregar a página
  useEffect(() => {
    if (folderName) {
      fetchFiles();
    }
  }, [folderName]);

  const fetchFiles = async () => {
    if (!folderName) return;

    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/folders/${folderName}/files/`,
        {
          method: "GET",
          credentials: "include", // Garantir que o cookie de autenticação seja enviado
        }
      );

      if (response.ok) {
        const data = await response.json();
        setFiles(data || []); // Atualiza os arquivos
      } else {
        console.error("Erro na resposta da API", response);
        alert('Erro ao carregar arquivos.');
      }
    } catch (error) {
      console.error("Erro ao buscar arquivos:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const data = await uploadFile(folderName, file);
      if (data) {
        fetchFiles(); // Refaz a busca dos arquivos após o upload
      }
    } catch (error) {
      console.error("Erro no upload:", error);
    }
  };

  const handleFileDownload = (filePath, fileName) => {
    // Chama a função de download passando a pasta e o nome do arquivo
    downloadFile(folderName, fileName);
  };

  return (
    <div>
      <h1>Pasta: {folderName}</h1>
      {/* Botão para abrir seletor de arquivo */}
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileUpload}
      />
      <button onClick={() => fileInputRef.current.click()}>📤 Fazer Upload</button>

      {/* Lista de arquivos */}
      {loading ? (
        <p>Carregando arquivos...</p>
      ) : files.length > 0 ? (
        <ul>
          {files.map((file, index) => {
            return (
              <li key={index}>
                {file.filename}
                <button onClick={() => handleFileDownload(file.file_path, file.filename)}>
                  Baixar
                </button>
              </li>
            );
          })}
        </ul>
      ) : (
        <p>Nenhum arquivo encontrado.</p>
      )}
    </div>
  );
}

export default FolderPage;
