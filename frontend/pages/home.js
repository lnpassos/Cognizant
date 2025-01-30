import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

function HomePage() {
  const [folderName, setFolderName] = useState('');
  const [file, setFile] = useState(null);
  const [folders, setFolders] = useState([]);
  const [error, setError] = useState(null); // Adicionado para exibir mensagens de erro
  const router = useRouter(); 

  useEffect(() => {
    fetchFolders(); 
  }, []);

  const fetchFolders = async () => {
  try {
    // Verifique primeiro se o usuário tem um token válido
    const homeResponse = await fetch('http://localhost:8000/home/', {
      method: 'GET',
      credentials: 'include', // Inclui o cookie com o token
    });

    if (homeResponse.status === 401) {
      // Se o token for inválido ou expirado, redireciona para a página de sessão expirada
      router.push("/session-expired");  // Redireciona para a página "Sessão Expirada"
      return;
    }

    // Caso o token seja válido, faz a requisição para buscar as pastas
    const response = await fetch('http://localhost:8000/folders/', {
      method: 'GET',
      credentials: 'include', // Inclui o cookie com o token
    });

    if (response.status === 400) {
      // Caso o erro seja relacionado a folders não encontradas ou sem permissão
      setError('Não há pastas disponíveis ou você não tem permissão para acessar.');
      return;
    }

    if (response.ok) {
      const data = await response.json();
      setFolders(data); // Atualiza a lista de pastas
    }
    
  } catch (error) {
    setError('Erro ao buscar pastas. Tente novamente mais tarde.');
  }
};


  const handleFolderCreate = async () => {
    if (!folderName) {
      setError('Por favor, insira um nome para a pasta');
      return;
    }

    const formData = new FormData();
    formData.append('folder_path', folderName); 
    if (file) {
      formData.append('file', file);
    }

    const response = await fetch('http://localhost:8000/create_folder/', {
      method: 'POST',
      body: formData,
      credentials: 'include',
    });

    if (response.status === 401) {
      setError('Token expirado, por favor faça login novamente.');
      router.push('/'); // Redireciona para a raiz
      return;
    }

    if (response.ok) {
      setError(null); // Limpa erro em caso de sucesso
      alert('Pasta criada com sucesso!');
      setFolderName('');
      setFile(null);
      fetchFolders(); 
    } else {
      const errorData = await response.json();
      setError(errorData.detail || 'Erro desconhecido');
    }
  };

  return (
    <div>
      <h1>Crie uma nova pasta</h1>
      {error && <div style={{ color: 'red' }}>{error}</div>} {/* Exibe erro, se houver */}
      <input
        type="text"
        value={folderName}
        onChange={(e) => setFolderName(e.target.value)}
        placeholder="Nome da pasta"
      />
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleFolderCreate}>Criar Pasta</button>

      <h2>Minhas Pastas</h2>
      {folders.length > 0 ? (
        <ul>
          {folders.map((folder) => (
            <li key={folder.id}>
              <a href={`/folders/${folder.path}`}>{folder.path}</a>
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
