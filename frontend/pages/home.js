import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { toast } from "react-toastify"; // Importa o Toast
import Header from "../components/Header";
import FolderItem from "../components/FolderItem";
import CustomFileInput from "../components/UploadFile";
import SearchFilter from "../components/SearchFilter"; // Importa o componente de filtro
import Pagination from "../components/Pagination";
import styles from '../styles/Home.module.css';

function HomePage() {
  const [folderName, setFolderName] = useState('');
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [filteredFolders, setFilteredFolders] = useState([]);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const router = useRouter();
  const ITEMS_PER_PAGE = 10;

  let resetFileInput = () => {}; 

  useEffect(() => {
    fetchFolders();
  }, []);

  const fetchFolders = async () => {
    try {
      const homeResponse = await fetch('http://localhost:8000/home/', { 
        method: 'GET',
        credentials: 'include',
      });

      if (homeResponse.status === 401) {
        router.push("/NotAuth");
        return;
      }

      const homeResponseFolders = await fetch('http://localhost:8000/folders/', {
        method: 'GET',
        credentials: 'include',
      });

      if (homeResponseFolders.status === 401) {
        router.push("/NotAuth");
        return;
      }

      if (homeResponseFolders.ok) { 
        const data = await homeResponseFolders.json();
        setFolders(data);
        setFilteredFolders(data);
      }
    } catch (error) {
      toast.error("Erro ao buscar pastas.");
    }
  };

  const handleSearchChange = (searchQuery) => {
    const filtered = folders.filter((folder) =>
      folder.path.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredFolders(filtered);
  };

  const handleFolderCreate = async () => {
    if (!folderName) {
      toast.error("Por favor, insira um nome para a pasta");
      return;
    }

    const formData = new FormData();
    formData.append("folder_path", folderName);

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("http://localhost:8000/create_folder/", {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (response.status === 401) {
        router.push("/NotAuth");
        return;
      }

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);

        setFolderName("");
        setFiles([]);
        resetFileInput();

        fetchFolders();
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || "Erro desconhecido");
      }
    } catch (error) {
      toast.error("Erro ao criar pasta.");
    }
  };

  const handleFolderDelete = async (folderPath) => {
    const encodedFolderPath = encodeURIComponent(folderPath);

    const response = await fetch(`http://localhost:8000/delete_folder/${encodedFolderPath}`, {
      method: 'DELETE',
      credentials: 'include',
    });

    if (response.status === 401) {
      router.push("/NotAuth");
      return;
    }

    if (response.ok) {
      toast.success("Pasta deletada com sucesso!");
      fetchFolders();
    } else {
      const errorData = await response.json();
      toast.error(errorData.detail || "Erro desconhecido");
    }
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
            <CustomFileInput 
              onFileSelect={setFiles} 
              resetInput={(resetFn) => (resetFileInput = resetFn)} 
            />
            <button className={styles.button} onClick={handleFolderCreate}>Send</button>
          </div>
        </div>
      </div>

      <div className={styles.bottomSection}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <SearchFilter onSearchChange={handleSearchChange} className={styles.searchFilter} />
        </div>

        {paginatedFolders.length > 0 ? (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "75px" }}>
            {paginatedFolders.map((folder) => (
              <FolderItem key={folder.id} folder={folder} onDelete={handleFolderDelete} />
            ))}
          </div>
        ) : (
          <p>Você ainda não tem pastas.</p>
        )}
        
        <Pagination
          totalItems={totalFolders}
          itemsPerPage={ITEMS_PER_PAGE}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
        />
      </div>
    </div>
  );
}

export default HomePage;
