import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import { uploadFile, downloadFile } from "../api/folder";
import Header from "../../components/Header";
import SearchFilter from "../../components/SearchFilter"; // Importando o componente de filtro
import styles from "../../styles/Files.module.css";

const supportedFormats = ["jpg", "jpeg", "png", "gif", "svg", "webp", "pdf", "mp4", "webm", "ogg", "mp3", "wav", "md"];

function FolderPage() {
  const router = useRouter();
  const { path } = router.query;
  const folderPath = Array.isArray(path) ? path.join("/") : "";
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef(null);
  const [filteredFiles, setFilteredFiles] = useState([]); // Estado para armazenar os arquivos filtrados
  const [searchQuery, setSearchQuery] = useState(""); // Estado para armazenar o valor da busca

  useEffect(() => {
    if (folderPath) {
      fetchFiles();
    }
  }, [folderPath]);

  useEffect(() => {
    if (searchQuery === "") {
      setFilteredFiles(files); // Quando a busca estiver vazia, mostrar todos os arquivos
    } else {
      setFilteredFiles(
        files.filter((file) =>
          file.filename.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    }
  }, [searchQuery, files]);

  const fetchFiles = async () => {
    if (!folderPath) return;
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/folders/${encodeURIComponent(folderPath)}/files/`,
        { method: "GET", credentials: "include" }
      );

      if (response.status === 401) {
        router.push("/session-expired");
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

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files.length || !folderPath) return;

    try {
      const uploadPromises = Array.from(files).map((file) =>
        uploadFile(folderPath, file)
      );

      await Promise.all(uploadPromises);
      await fetchFiles();
    } catch (error) {
      console.error("Erro no upload:", error);
    }

    event.target.value = "";
  };

  const handleFileDownload = (fileName) => {
    if (!folderPath) return;
    downloadFile(folderPath, fileName);
  };

  const handleFileDelete = async (fileName) => {
    if (!folderPath || !fileName) return;
    try {
      const response = await fetch(
        `http://localhost:8000/delete_file/${encodeURIComponent(
          folderPath
        )}/${encodeURIComponent(fileName)}`,
        { method: "DELETE", credentials: "include" }
      );

      if (response.ok) {
        fetchFiles();
      } else {
        const errorData = await response.json();
        alert(errorData.detail || "Erro ao deletar arquivo");
      }
    } catch (error) {
      console.error("Erro ao deletar arquivo:", error);
    }
  };

  const previewFile = (folderPath, fileName) => {
    if (!folderPath || !fileName) return;
    const fileExtension = fileName.split('.').pop().toLowerCase();

    // Verificar se o formato do arquivo é suportado
    if (supportedFormats.includes(fileExtension)) {
      const fileUrl = `http://localhost:8000/preview/${encodeURIComponent(
        folderPath
      )}/${encodeURIComponent(fileName)}`;
      window.open(fileUrl, "_blank"); // Abre o arquivo em uma nova aba
    } else {
      alert('Formato de arquivo não suportado para visualização direta.');
    }
  };

  const handleSearchChange = (query) => {
    setSearchQuery(query);
  };

  return (
    <>
      <Header />
      <div className={styles.folderContainer}>
        <div className={styles.filterSection}>
          <h1 className={styles.folderTitle}>/{folderPath || "Carregando..."}</h1>
          <SearchFilter
            className={styles.searchFilter}
            onSearchChange={handleSearchChange} // Passando a função de busca
          />
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            multiple
            onChange={handleFileUpload}
          />
          <button
            className={styles.uploadButton}
            onClick={() => fileInputRef.current.click()}
          >
            📤 New file
          </button>
        </div>

        {loading ? (
          <p>Carregando arquivos...</p>
        ) : filteredFiles.length > 0 ? (
          <ul className={styles.fileList}>
            {filteredFiles.map((file, index) => {
              const fileExtension = file.filename.split('.').pop().toLowerCase();
              const isViewable = supportedFormats.includes(fileExtension); // Verifica se o arquivo é visualizável

              return (
                <li key={index} className={styles.fileItem}>
                  <span
                    onClick={() => previewFile(folderPath, file.filename)}
                    className={styles.fileName}
                    title={file.filename} // Tooltip mostrando o nome do arquivo
                  >
                    {file.filename}
                  </span>
                  <div className={styles.fileActions}>
                    {/* Exibe o ícone de visualização apenas se o formato for suportado */}
                    {isViewable && (
                      <button
                        className={styles.actionButton}
                        onClick={() => previewFile(folderPath, file.filename)}
                        title="Visualizar arquivo" // Tooltip para visualizar
                      >
                        👁️
                      </button>
                    )}
                    <button
                      className={styles.actionButton}
                      onClick={() => handleFileDownload(file.filename)}
                      title="Baixar arquivo" // Tooltip para baixar
                    >
                      📥
                    </button>
                    <button
                      className={styles.actionButton}
                      onClick={() => handleFileDelete(file.filename)}
                      title="Deletar arquivo" // Tooltip para deletar
                    >
                      ❌
                    </button>
                  </div>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className={styles.noFilesMessage}>Nenhum arquivo encontrado.</p>
        )}
      </div>
    </>
  );
}

export default FolderPage;
