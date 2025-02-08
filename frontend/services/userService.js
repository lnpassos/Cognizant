const API_BASE_URL = "http://localhost:8000";

export const loginUser = async (email, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/login/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Erro ao fazer login.");
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || "Erro desconhecido.");
  }
};

export const registerUser = async (username, email, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/register/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Erro ao registrar usuário.");
    }

    return await response.json();
  } catch (error) {
    throw new Error(error.message || "Erro desconhecido.");
  }
};
