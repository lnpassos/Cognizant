import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

function HomePage() {
  const [folderName, setFolderName] = useState('');
  const [files, setFiles] = useState([]);
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null);
  const [fileInputKey, setFileInputKey] = useState(Date.now()); // Força recriação do input
  const router = useRouter();

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

  const handleFolderCreate = async () => {
    if (!folderName) {
      setError("Por favor, insira um nome para a pasta");
      return;
    }

    const formData = new FormData();
    formData.append("folder_path", folderName);

    if (files.length > 0) {
      files.forEach((file) => {
        formData.append("files", file);
      });
    }

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
        alert("Pasta criada com sucesso!");

        setFolderName("");
        setFiles([]);
        setFileInputKey(Date.now()); // Atualiza a chave para resetar o input

        fetchFolders();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Erro desconhecido");
      }
    } catch (error) {
      setError("Erro ao criar pasta.");
    }
  };

  const handleFileChange = (event) => {
    setFiles(Array.from(event.target.files));
  };

  const handleFolderDelete = async (folderPath) => {
    const response = await fetch(`http://localhost:8000/delete_folder/${folderPath}`, {
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
      fetchFolders();
    } else {
      const errorData = await response.json();
      setError(errorData.detail || 'Erro desconhecido');
    }
  };

  return (
    <div>
      <h1>Crie uma nova pasta</h1>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <input
        type="text"
        value={folderName}
        onChange={(e) => setFolderName(e.target.value)}
        placeholder="Nome da pasta"
      />
      <input
        key={fileInputKey} // Reseta o input ao mudar a key
        type="file"
        multiple
        onChange={handleFileChange}
      />
      <button onClick={handleFolderCreate}>Criar Pasta</button>

      <h2>Minhas Pastas</h2>
      {folders.length > 0 ? (
        <ul>
          {folders.map((folder) => (
            <li key={folder.id}>
              <a href={`/folders/${folder.path}`}>{folder.path}</a>
              <button onClick={() => handleFolderDelete(folder.path)} style={{ marginLeft: '10px' }}>
                Deletar
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p>Você ainda não tem pastas.</p>
      )}
    </div>
  );
}

export default HomePage;
