import { useState } from "react";
import axios from "axios";
import Modal from "react-modal";

Modal.setAppElement("#__next");

export default function Home() {
  const [isLoginModalOpen, setLoginModalOpen] = useState(false);
  const [isRegisterModalOpen, setRegisterModalOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const response = await axios.post("http://localhost:8000/login/", {
        username,
        password,
      }, { withCredentials: true }); // Envia cookies com a requisição

      alert(response.data.message);
      window.location.href = "/home"; // Redireciona para a página de "Bem-vindo"
    } catch (error) {
      alert(error.response?.data?.detail || "Login failed");
    }
  };

  const handleRegister = async () => {
    try {
      const response = await axios.post("http://localhost:8000/register/", {
        username,
        email,
        password,
      }, { withCredentials: true });

      alert("Conta criada com sucesso!");
      setRegisterModalOpen(false);
      window.location.href = "/home"; // Redireciona após criar conta
    } catch (error) {
      alert(error.response?.data?.detail || "Falha ao criar conta!");
    }
  };

  return (
    <div>
      <h1>Home</h1>
      <button onClick={() => setLoginModalOpen(true)}>Login</button>
      <button onClick={() => setRegisterModalOpen(true)}>Criar conta</button>

      {/* Modal Login */}
      <Modal
        isOpen={isLoginModalOpen}
        onRequestClose={() => setLoginModalOpen(false)}
        className="react-modal-content"
        overlayClassName="react-modal-overlay"
      >
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button onClick={handleLogin}>Login</button>
        <button
          onClick={() => setLoginModalOpen(false)}
          className="close"
        >
          Close
        </button>
      </Modal>

      {/* Modal Register */}
      <Modal
        isOpen={isRegisterModalOpen}
        onRequestClose={() => setRegisterModalOpen(false)}
        className="react-modal-content"
        overlayClassName="react-modal-overlay"
      >
        <h2>Criar conta</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button onClick={handleRegister}>Criar conta</button>
        <button
          onClick={() => setRegisterModalOpen(false)}
          className="close"
        >
          Close
        </button>
      </Modal>
    </div>
  );
}
