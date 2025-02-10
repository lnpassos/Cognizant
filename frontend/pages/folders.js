import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { toast } from "react-toastify";
import { fetchFolders, createFolder, deleteFolder } from "../services/folderService";
import Header from "../components/Header";
import FolderItem from "../components/FolderItem";
import CustomFileInput from "../components/UploadFile";
import SearchFilter from "../components/SearchFilter";
import Pagination from "../components/Pagination";
import DeleteConfirmationModal from "../components/DeleteConfirmationModal";
import styles from "../styles/Home.module.css";

function HomePage() {
  const [folderName, setFolderName] = useState("");
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [filteredFolders, setFilteredFolders] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [folderToDelete, setFolderToDelete] = useState(null);
  const router = useRouter();
  const ITEMS_PER_PAGE = 10;

  let resetFileInput = () => {};

  useEffect(() => {
    loadFolders();
  }, []);

  const loadFolders = async () => {
    try {
      const data = await fetchFolders();

      if (data.unauthorized) {
        router.push("/NotAuth");
        return;
      }

      setFolders(data);
      setFilteredFolders(data);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleSearchChange = (searchQuery) => {
    const filtered = folders.filter((folder) =>
      folder.path.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredFolders(filtered);
  };

  const handleFolderCreate = async () => {
    try {
      const data = await createFolder(folderName, files);

      if (data.unauthorized) {
        router.push("/NotAuth");
        return;
      }

      toast.success(data.message);
      setFolderName("");
      setFiles([]);
      resetFileInput();
      loadFolders();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleFolderDelete = async (folderPath) => {
    try {
      const data = await deleteFolder(folderPath);

      if (data.unauthorized) {
        router.push("/NotAuth");
        return;
      }

      toast.success("Folder successfully deleted!");
      loadFolders();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const confirmDelete = async () => {
    if (folderToDelete) {
      await handleFolderDelete(folderToDelete);
    }

    setIsDeleteModalOpen(false);
    setFolderToDelete(null);
  };

  const cancelDelete = () => {
    setIsDeleteModalOpen(false);
    setFolderToDelete(null);
  };

  const totalFolders = filteredFolders.length;
  const totalPages = Math.ceil(totalFolders / ITEMS_PER_PAGE);
  const paginatedFolders = filteredFolders.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  return (
    <div className={styles.container}>
      <Header />
      <div className={styles.folderSection}>
        <div className={styles.topSection}>
          <input
            className={styles.inputField}
            type="text"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            placeholder="Insert a URL"
          />
          <div className={styles.uploadContainer}>
            <CustomFileInput onFileSelect={setFiles} resetInput={(resetFn) => (resetFileInput = resetFn)} />
            <button className={styles.button} onClick={handleFolderCreate}>
              Send
            </button>
          </div>
        </div>
      </div>

      <div className={styles.bottomSection}>
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <SearchFilter onSearchChange={handleSearchChange} className={styles.searchFilter} />
        </div>

        {paginatedFolders.length > 0 ? (
          <>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "75px" }}>
              {paginatedFolders.map((folder) => (
                <FolderItem key={folder.id} folder={folder} onDelete={handleFolderDelete} />
              ))}
            </div>
            <Pagination totalItems={totalFolders} itemsPerPage={ITEMS_PER_PAGE} currentPage={currentPage} onPageChange={setCurrentPage} />
          </>
        ) : (
          <p className={styles.noFoldersMessage}>No files found.</p>
        )}
      </div>

      <DeleteConfirmationModal isOpen={isDeleteModalOpen} onConfirm={confirmDelete} onCancel={cancelDelete} folderToDelete={folderToDelete} />
    </div>
  );
}

export default HomePage;
