import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import Header from "../../components/Header";
import SearchFilter from "../../components/SearchFilter";
import Pagination from "../../components/Pagination";
import DeleteConfirmationModal from "../../components/DeleteConfirmationModal";
import styles from "../../styles/Files.module.css";
import { toast } from "react-toastify";
import {
  fetchFiles,
  handleFileUpload,
  handleFileDownload,
  handleFileDelete,
  previewFile
} from "../../services/fileService";

const ITEMS_PER_PAGE = 6;

const supportedViewableFormats = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'md'];

const isViewableFile = (filename) => {
  const fileExtension = filename.split('.').pop().toLowerCase();
  return supportedViewableFormats.includes(fileExtension);
};

function FolderPage() {
  const router = useRouter();
  const { path } = router.query;
  const folderPath = Array.isArray(path) ? path.join("/") : "";

  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filteredFiles, setFilteredFiles] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    if (folderPath) fetchFiles(folderPath, router, setFiles, setLoading, setError);
  }, [folderPath]);

  useEffect(() => {
    if (searchQuery === "") {
      setFilteredFiles(files);
    } else {
      setFilteredFiles(files.filter(file =>
        file.filename.toLowerCase().includes(searchQuery.toLowerCase())
      ));
    }
    setCurrentPage(1);
  }, [searchQuery, files]);

  const handleDeleteClick = (fileName) => {
    setFileToDelete(fileName);
    setIsModalOpen(true);
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
          <SearchFilter className={styles.searchFilter} onSearchChange={setSearchQuery} />
          <input type="file" ref={fileInputRef} style={{ display: "none" }} multiple
            onChange={(e) => handleFileUpload(e, folderPath, () => fetchFiles(folderPath, router, setFiles, setLoading, setError), router)}
          />
          <button className={styles.uploadButton} onClick={() => fileInputRef.current.click()}>
            📤 New file
          </button>
        </div>

        {loading ? <p>Loading files...</p> : paginatedFiles.length > 0 ? (
          <>
            <ul className={styles.fileList}>
              {paginatedFiles.map((file, index) => (
                <li key={index} className={styles.fileItem}>
                  <span onClick={() => previewFile(folderPath, file.filename, file.revision, router)}
                        className={styles.fileName} title={file.filename}>
                    {file.filename}
                  </span>
                  <div className={styles.fileActions}>
                    {isViewableFile(file.filename) && (
                      <button className={styles.actionButton} onClick={() => previewFile(folderPath, file.filename, file.revision)} title="Visualizar arquivo">👁️</button>
                    )}
                    <button className={styles.actionButton} onClick={() => handleFileDownload(folderPath, file.filename, router)} title="Baixar arquivo">📥</button>
                    <button className={styles.actionButton} onClick={() => handleDeleteClick(file.filename)} title="Deletar arquivo">❌</button>
                  </div>
                </li>
              ))}
            </ul>

            <Pagination totalItems={totalFiles} itemsPerPage={ITEMS_PER_PAGE} currentPage={currentPage} onPageChange={setCurrentPage} />
          </>
        ) : <p className={styles.noFilesMessage}>No files found.</p>}
      </div>

      <DeleteConfirmationModal isOpen={isModalOpen} onConfirm={() => handleFileDelete(folderPath, fileToDelete, () => fetchFiles(folderPath, router, setFiles, setLoading, setError), router, toast, setIsModalOpen)} onCancel={() => setIsModalOpen(false)} />
    </>
  );
}

export default FolderPage;
