import { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    axios
      .get("http://localhost:8000/home/", { withCredentials: true })
      .then((response) => {
        setUsername(response.data.message);
      })
      .catch((error) => {
        setError("Sessão expirada. Faça login novamente.");
        setTimeout(() => (window.location.href = "/"), 2000); // Redireciona para login
      });
  }, []);

  const handleLogout = () => {
    axios
      .post("http://localhost:8000/logout/", {}, { withCredentials: true })
      .then(() => {
        window.location.href = "/"; // Redireciona para login
      });
  };

  return (
    <div>
      {error ? (
        <h1>{error}</h1>
      ) : (
        <>
          <h1>{username}</h1>
          <button onClick={handleLogout}>Logout</button>
        </>
      )}
    </div>
  );
}
