/*
export async function uploadFile(folderName, file) {
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const response = await fetch(`http://localhost:8000/upload/${encodeURIComponent(folderName)}`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });
  
      if (!response.ok) {
        throw new Error("Falha no upload");
      }
  
      return await response.json();
    } catch (error) {
      console.error("Erro no upload:", error);
    }
  }
  
  export async function downloadFile(folderName, fileName) {
    try {
      const response = await fetch(`http://localhost:8000/download/${encodeURIComponent(folderName)}/${encodeURIComponent(fileName)}`, {
        method: "GET",
        credentials: "include",
      });
  
      if (!response.ok) {
        throw new Error("Falha no download");
      }
  
      const blob = await response.blob();
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = fileName;
      link.click();
    } catch (error) {
      console.error("Erro no download:", error);
    }
  }
  */