const API_BASE_URL = "http://localhost:8000";

export const fetchFolders = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/folders/`, {
      method: "GET",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (response.status === 401) {
      return { unauthorized: true };
    }

    if (!response.ok) {
      throw new Error("Error fetching folders.");
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || "Unknown error.");
  }
};

export const createFolder = async (folderName, files) => {
  try {
    if (!folderName) {
      throw new Error("Please enter a name for the folder.");
    }

    const formData = new FormData();
    formData.append("folder_path", folderName);

    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await fetch(`${API_BASE_URL}/create_folder/`, {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    if (response.status === 401) {
      return { unauthorized: true };
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error creating folder.");
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || "Unknown error.");
  }
};

export const deleteFolder = async (folderPath) => {
  try {
    const encodedFolderPath = encodeURIComponent(folderPath);
    const response = await fetch(`${API_BASE_URL}/delete_folder/${encodedFolderPath}`, {
      method: "DELETE",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
    });

    if (response.status === 401) {
      return { unauthorized: true };
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error deleting folder.");
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || "Unknown error.");
  }
};
