import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import Header from "../../components/Header";
import SearchFilter from "../../components/SearchFilter";
import Pagination from "../../components/Pagination";
import DeleteConfirmationModal from "../../components/DeleteConfirmationModal";
import styles from "../../styles/Files.module.css";
import { toast } from "react-toastify";

const supportedFormats = ["jpg", "jpeg", "png", "gif", "svg", "webp", "pdf", "mp4", "webm", "ogg", "mp3", "wav", "md"];
const ITEMS_PER_PAGE = 7;

function FolderPage() {
  const router = useRouter();
  const { path } = router.query;
  const folderPath = Array.isArray(path) ? path.join("/") : "";
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const [filteredFiles, setFilteredFiles] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);

  useEffect(() => {
    if (folderPath) {
      fetchFiles();
    }
  }, [folderPath]);

  useEffect(() => {
    if (searchQuery === "") {
      setFilteredFiles(files);
    } else {
      setFilteredFiles(
        files.filter((file) =>
          file.filename.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    }
    setCurrentPage(1);
  }, [searchQuery, files]);

  const fetchFiles = async () => {
    if (!folderPath) return;
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/folders/${encodeURIComponent(folderPath)}/files/`,
        { method: "GET", 
          credentials: "include" ,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.status === 401) {
        router.push("/NotAuth");
        return;
      }

      if (response.status === 403) {
        router.push("/AccessDenied");
        return;
      }

      if (!response.ok) {
        throw new Error("Erro ao buscar arquivos.");
      }

      const filesData = await response.json();
      setFiles(filesData);
    } catch (error) {
      setError("Ocorreu um erro ao carregar os arquivos.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files.length || !folderPath) return;

    try {
      const formData = new FormData();
      Array.from(files).forEach(file => formData.append("file", file));

      const response = await fetch(`http://localhost:8000/upload/${folderPath}`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (response.status === 401) {
        router.push("/NotAuth");
        return;
      }

      if (response.status === 403) {
        router.push("/AccessDenied");
        return;
      }

      if (!response.ok) {
        throw new Error("Falha no upload");
      }

      await response.json();
      await fetchFiles();
    } catch (error) {
      console.error("Erro no upload:", error);
    }

    event.target.value = "";
  };

  const handleFileDownload = (fileName) => {
    if (!folderPath) return;
  
    fetch(`http://localhost:8000/download/${folderPath}/${fileName}`, {
      method: "GET",
      credentials: "include",
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then(response => {
        if (response.status === 401) {

          router.push("/NotAuth");
          return;
        }
  
        if (!response.ok) {
          throw new Error('Falha na requisição');
        }
  
        return response.blob();
      })
      .then(blob => {
        if (blob) {
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = fileName;
          link.click();
        }
      })
      .catch(error => console.error('Erro no download:', error));
  };
  

  const handleFileDeleteClick = (fileName) => {
    setFileToDelete(fileName);
    setIsModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!folderPath || !fileToDelete) return;
    try {
      const response = await fetch(
        `http://localhost:8000/delete_file/${encodeURIComponent(
          folderPath
        )}/${encodeURIComponent(fileToDelete)}`,
        { method: "DELETE", 
          credentials: "include" ,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.status === 401) {
        router.push("/NotAuth");
        return;
      }

      if (response.ok) {
        fetchFiles();
        toast.success(`Arquivo "${fileToDelete}" deletado com sucesso!`);
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || "Erro ao deletar arquivo");
      }
    } catch (error) {
      console.error("Erro ao deletar arquivo:", error);
      toast.error("Ocorreu um erro ao deletar o arquivo.");
    } finally {
      setIsModalOpen(false);
    }
  };

  const handleCancelDelete = () => {
    setIsModalOpen(false);
  };

  const encodePath = (path) => {
    // I am using this function to keep the URL as requested in the description
    return path.split('/').map(encodeURIComponent).join('/');
  };

const previewFile = (folderPath, fileName, revision) => {
    if (!folderPath || !fileName) return;
    const fileExtension = fileName.split('.').pop().toLowerCase();

    if (supportedFormats.includes(fileExtension)) {

        /* Here we could use encodeURIComponent directly, but it would encode
           slashes ('/') as '%2F', which would make the URL messy and unreadable.
           That's why we use the encodePath function to keep the slashes intact. */

        const fileUrl = `http://localhost:8000/folders/${encodePath(
            folderPath
        )}/${encodeURIComponent(fileName)}?revision=${revision}`;

        fetch(fileUrl, {
            method: "GET",
            credentials: "include",
            headers: {
              'Content-Type': 'application/json',
            },
        })
            .then(response => {
                if (response.status === 401) {
                    router.push("/NotAuth");
                    return;
                }

                if (response.ok) {
                    window.open(fileUrl, "_blank");
                } else {
                    console.error("Erro ao acessar o arquivo.");
                }
            })
            .catch(error => console.error('Erro ao visualizar arquivo:', error));
    }
};
  

  const handleSearchChange = (query) => {
    setSearchQuery(query);
  };

  const totalFiles = filteredFiles.length;
  const totalPages = Math.ceil(totalFiles / ITEMS_PER_PAGE);

  const paginatedFiles = filteredFiles.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  return (
    <>
      <Header />
      <div className={styles.folderContainer}>
        <div className={styles.filterSection}>
          <h1 className={styles.folderTitle}>/{folderPath || "Carregando..."}</h1>
          <SearchFilter
            className={styles.searchFilter}
            onSearchChange={handleSearchChange}
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
          <p>Loading files...</p>
        ) : paginatedFiles.length > 0 ? (
          <>
            <ul className={styles.fileList}>
              {paginatedFiles.map((file, index) => {
                const fileExtension = file.filename.split('.').pop().toLowerCase();
                const isViewable = supportedFormats.includes(fileExtension);

                return (
                  <li key={index} className={styles.fileItem}>
                    <span
                      onClick={() => previewFile(folderPath, file.filename, file.revision)}
                      className={styles.fileName}
                      title={file.filename}
                    >
                      {file.filename}
                    </span>
                    <div className={styles.fileActions}>
                      {isViewable && (
                        <button
                          className={styles.actionButton}
                          onClick={() => previewFile(folderPath, file.filename, file.revision)}
                          title="Visualizar arquivo"
                        >
                          👁️
                        </button>
                      )}
                      <button
                        className={styles.actionButton}
                        onClick={() => handleFileDownload(file.filename)}
                        title="Baixar arquivo"
                      >
                        📥
                      </button>
                      <button
                        className={styles.actionButton}
                        onClick={() => handleFileDeleteClick(file.filename)}
                        title="Deletar arquivo"
                      >
                        ❌
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>

            <Pagination
              totalItems={totalFiles}
              itemsPerPage={ITEMS_PER_PAGE}
              currentPage={currentPage}
              onPageChange={setCurrentPage}
            />
          </>
        ) : (
          <p className={styles.noFilesMessage}>No files found.</p>
        )}
      </div>

      <DeleteConfirmationModal
        isOpen={isModalOpen}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        folderToDelete={fileToDelete}
      />
    </>
  );
}

export default FolderPage;
