import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Header from "../components/Header";
import FolderItem from "../components/FolderItem";
import CustomFileInput from "../components/UploadFile"; 
import styles from '../styles/Home.module.css'; 

function HomePage() {
  const [folderName, setFolderName] = useState('');
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null);
  const router = useRouter();

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
      }
    } catch (error) {
      setError('Erro ao buscar pastas. Tente novamente mais tarde.');
    }
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
        <h2 className={styles.subtitle}>Folders</h2>
        {folders.length > 0 ? (
          <div style={{ display: "flex", flexWrap: "wrap", gap: "75px" }}>
            {folders.map((folder) => (
              <FolderItem key={folder.id} folder={folder} onDelete={handleFolderDelete} />
            ))}
          </div>
        ) : (
          <p>Você ainda não tem pastas.</p>
        )}
      </div>
    </div>
  );
}

export default HomePage;
