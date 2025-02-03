import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Header from "../components/Header";
import FolderItem from "../components/FolderItem";
import CustomFileInput from "../components/UploadFile";
import SearchFilter from "../components/SearchFilter"; // Importa o componente de filtro
import styles from '../styles/Home.module.css';
import Pagination from "../components/Pagination";

function HomePage() {
  const [folderName, setFolderName] = useState('');
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [filteredFolders, setFilteredFolders] = useState([]); // Novo estado para pastas filtradas
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1); // Estado para controlar a página atual
  const router = useRouter();
  const ITEMS_PER_PAGE = 10;

  let resetFileInput = () => {}; // Variável para armazenar a função de reset

  // Carregar pastas ao carregar a página
  useEffect(() => {
    fetchFolders();
  }, []);

  // Função para buscar pastas do servidor
  const fetchFolders = async () => {
    try {
      const homeResponse = await fetch('http://localhost:8000/home/', {
        method: 'GET',
        credentials: 'include',
      });

      if (homeResponse.status === 401) {
        router.push("/session-expired");
        return;
      }

      const response = await fetch('http://localhost:8000/folders/', {
        method: 'GET',
        credentials: 'include',
      });

      if (response.status === 400) {
        setError('Não há pastas disponíveis ou você não tem permissão para acessar.');
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setFolders(data);
        setFilteredFolders(data); // Inicializa as pastas filtradas com todos os dados
      }
    } catch (error) {
      setError('Erro ao buscar pastas. Tente novamente mais tarde.');
    }
  };

  // Função para atualizar o filtro de pesquisa
  const handleSearchChange = (searchQuery) => {
    const filtered = folders.filter((folder) =>
      folder.path.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredFolders(filtered); // Atualiza a lista de pastas filtradas
  };

  // Criar uma nova pasta e, opcionalmente, enviar arquivos
  const handleFolderCreate = async () => {
    if (!folderName) {
      setError("Por favor, insira um nome para a pasta");
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
        setError("Token expirado, por favor faça login novamente.");
        router.push("/");
        return;
      }

      if (response.ok) {
        setError(null);
        const data = await response.json();
        alert(data.message);

        setFolderName("");
        setFiles([]);
        resetFileInput(); // Reseta o input de arquivos

        fetchFolders();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Erro desconhecido");
      }
    } catch (error) {
      setError("Erro ao criar pasta.");
    }
  };

  // Excluir uma pasta do servidor
  const handleFolderDelete = async (folderPath) => {
    const encodedFolderPath = encodeURIComponent(folderPath); 

    const response = await fetch(`http://localhost:8000/delete_folder/${encodedFolderPath}`, {
      method: 'DELETE',
      credentials: 'include',
    });

    if (response.status === 401) {
      setError('Token expirado, por favor faça login novamente.');
      router.push('/');
      return;
    }

    if (response.ok) {
      alert('Pasta deletada com sucesso!');
      fetchFolders(); // Atualiza a lista de pastas após exclusão
    } else {
      const errorData = await response.json();
      setError(errorData.detail || 'Erro desconhecido');
    }
  };

  // Lógica de Paginação
  const totalFolders = filteredFolders.length;  // Número total de pastas
  const totalPages = Math.ceil(totalFolders / ITEMS_PER_PAGE); // Total de páginas
  const paginatedFolders = filteredFolders.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);  // Ajusta para a última página se a página atual for inválida
    }
  }, [currentPage, totalPages]);

  return (
    <div className={styles.container}>
      <Header />
      <div className={styles.folderSection}>
        <div className={styles.topSection}>
          <h1 className={styles.title}>Crie uma nova pasta</h1>
          {error && <div style={{ color: 'red' }}>{error}</div>}

          <input
            className={styles.inputField}
            type="text"
            value={folderName}
            onChange={(e) => setFolderName(e.target.value)}
            placeholder="Nome da pasta"
          />

          <div className={styles.uploadContainer}>
            <CustomFileInput 
              onFileSelect={setFiles} 
              resetInput={(resetFn) => (resetFileInput = resetFn)} 
            />
            <button className={styles.button} onClick={handleFolderCreate}>Criar Pasta</button>
          </div>
        </div>
      </div>

      <div className={styles.bottomSection}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <h2 className={styles.subtitle}>URL's</h2>
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
        
        {/* Componente de Paginação */}
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
