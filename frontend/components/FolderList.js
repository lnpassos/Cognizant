// components/FolderList.js
import { useState, useEffect } from 'react';

function FolderList() {
  const [folders, setFolders] = useState([]);

  useEffect(() => {
    const fetchFolders = async () => {
      const response = await fetch('http://localhost:8000/folders/', {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setFolders(data);
      }
    };

    fetchFolders();
  }, []);

  return (
    <div>
      <h2>Minhas Pastas</h2>
      <ul>
        {folders.map((folder) => (
          <li key={folder.name}>
            <a href={`/${folder.name}`}>{folder.name}</a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FolderList;
