// pages/home.js
import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

function HomePage() {
  const [folderName, setFolderName] = useState('');
  const [folders, setFolders] = useState([]);

  // Buscar pastas ao carregar a página
  useEffect(() => {
    const fetchFolders = async () => {
      try {
        const response = await fetch('http://localhost:8000/folders/', {
          method: 'GET',
          credentials: 'include', // Garantir que o cookie de autenticação seja enviado
        });

        if (response.ok) {
          const data = await response.json();
          setFolders(data); // Armazenar as pastas retornadas
        } else {
          alert('Erro ao carregar pastas.');
        }
      } catch (error) {
        console.error('Erro ao buscar pastas:', error);
      }
    };

    fetchFolders();
  }, []); // Esse efeito roda uma vez quando a página é carregada

  // Função para criar uma nova pasta
  const handleFolderCreate = async () => {
    if (!folderName) {
      alert('Por favor, insira um nome para a pasta');
      return;
    }

    const response = await fetch('http://localhost:8000/create_folder/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_name: folderName }),
      credentials: 'include', // Inclui o cookie com o token
    });

    if (response.ok) {
      alert('Pasta criada com sucesso!');
      setFolderName(''); // Limpa o campo de input
      // Atualiza a lista de pastas
      const newFolder = { name: folderName };
      setFolders((prevFolders) => [...prevFolders, newFolder]);
    } else {
      alert('Erro ao criar pasta.');
    }
  };

  return (
    <div>
      <h1>Crie uma nova pasta</h1>
      <input
        type="text"
        value={folderName}
        onChange={(e) => setFolderName(e.target.value)}
        placeholder="Nome da pasta"
      />
      <button onClick={handleFolderCreate}>Criar Pasta</button>

      <h2>Minhas Pastas</h2>
      {folders.length > 0 ? (
        <ul>
          {folders.map((folder) => (
            <li key={folder.name}>
              <a href={`folders/${folder.name}`}>{folder.name}</a>
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
