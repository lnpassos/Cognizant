export async function uploadFile(folderName, file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`http://localhost:8000/upload/${folderName}`, {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error("Falha no upload");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erro no upload:", error);
  }
}


export const deleteFile = async (folderPath, fileName) => {
  try {
    const response = await fetch(
      `http://localhost:8000/folders/${encodeURIComponent(folderPath)}/files/${encodeURIComponent(fileName)}`,
      {
        method: "DELETE",
        credentials: "include", // Inclui o cookie com o token
      }
    );
    return response;
  } catch (error) {
    throw new Error("Erro ao deletar arquivo");
  }
};



export async function downloadFile(folderName, fileName) {
  try {
    const response = await fetch(`http://localhost:8000/download/${folderName}/${fileName}`, {
      method: 'GET',
      credentials: 'include', // Envia cookies de autenticação, se necessário
    });
    
    if (!response.ok) {
      throw new Error('Falha no download');
    }

    const blob = await response.blob();
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = fileName; // Nome do arquivo para download
    link.click();
  } catch (error) {
    console.error('Erro no download:', error);
  }
}
