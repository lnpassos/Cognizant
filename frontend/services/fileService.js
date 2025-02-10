const API_BASE_URL = "http://localhost:8000";
const supportedFormats = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'txt', 'md'];

const encodePath = (path) => {
  return path.split('/').map(encodeURIComponent).join('/');
};

export const fetchFiles = async (folderPath, router, setFiles, setLoading, setError) => {
  if (!folderPath) return;
  setLoading(true);
  setError(null);

  try {
    const response = await fetch(`${API_BASE_URL}/folder/${encodePath(folderPath)}/files/`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (response.status === 401) return router.push("/NotAuth");
    if (response.status === 403) return router.push("/AccessDenied");
    if (!response.ok) throw new Error("Erro ao buscar arquivos.");

    const filesData = await response.json();
    setFiles(filesData);
  } catch {
    setError("Ocorreu um erro ao carregar os arquivos.");
  } finally {
    setLoading(false);
  }
};

export const handleFileUpload = async (event, folderPath, fetchFiles, router) => {
  const files = event.target.files;
  if (!files.length || !folderPath) return;

  try {
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append("file", file));

    const response = await fetch(`${API_BASE_URL}/upload/${encodePath(folderPath)}`, {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    if (response.status === 401) return router.push("/NotAuth");
    if (response.status === 403) return router.push("/AccessDenied");
    if (!response.ok) throw new Error("Falha no upload");

    await response.json();
    await fetchFiles();
  } catch (error) {
    console.error("Erro no upload:", error);
  }

  event.target.value = "";
};

export const handleFileDownload = (folderPath, fileName, router) => {
  if (!folderPath) return;

  fetch(`${API_BASE_URL}/download/${encodePath(folderPath)}/${encodeURIComponent(fileName)}`, {
    method: "GET",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
  })
    .then(response => {
      if (response.status === 401) return router.push("/NotAuth");
      if (!response.ok) throw new Error("Falha na requisição");

      return response.blob();
    })
    .then(blob => {
      if (blob) {
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = fileName;
        link.click();
      }
    })
    .catch(error => console.error("Erro no download:", error));
};

export const handleFileDelete = async (folderPath, fileToDelete, fetchFiles, router, toast, setIsModalOpen) => {
  if (!folderPath || !fileToDelete) return;

  try {
    const response = await fetch(`${API_BASE_URL}/delete_file/${encodePath(folderPath)}/${encodeURIComponent(fileToDelete)}`, {
      method: "DELETE",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (response.status === 401) return router.push("/NotAuth");
    if (response.ok) {
      fetchFiles();
      toast.success(`Arquivo "${fileToDelete}" deletado com sucesso!`);
    } else {
      const errorData = await response.json();
      toast.error(errorData.detail || "Erro ao deletar arquivo");
    }
  } catch (error) {
    console.error("Erro ao deletar arquivo:", error);
    toast.error("Ocorreu um erro ao deletar o arquivo.");
  } finally {
    setIsModalOpen(false);
  }
};

export const previewFile = (folderPath, fileName, revision, router) => {
    if (!folderPath || !fileName) return;
  
    const fileExtension = fileName.split('.').pop().toLowerCase();
  
    if (supportedFormats.includes(fileExtension)) {
      const fileUrl = `${API_BASE_URL}/folder/${encodePath(folderPath)}/${encodeURIComponent(fileName)}?revision=${revision}`;
  
      fetch(fileUrl, {
        method: "GET",
        credentials: "include",
        headers: { 
          "Content-Type": "application/json",
          "Cache-Control": "no-cache"  
        },
      })
        .then(response => {
          if (response.status === 401) {
            router.push("/NotAuth");
            return;
          }
  
          if (response.ok) {
            window.open(fileUrl, "_blank");
          } else {
            console.error("Erro ao acessar o arquivo.");
          }
        })
        .catch(error => console.error("Erro ao visualizar arquivo:", error));
    } else {
      console.error("Arquivo não suportado para visualização.");
    }
  };
  