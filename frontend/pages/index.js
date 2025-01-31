import { useState, useEffect } from "react";
import axios from "axios";
import Modal from "react-modal";

Modal.setAppElement("#__next");

export default function Home() {
  const [isLoginModalOpen, setLoginModalOpen] = useState(true);
  const [isRegisterModalOpen, setRegisterModalOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const response = await axios.post("http://localhost:8000/users/login/", {
        username,
        password,
      }, { withCredentials: true });

      alert(response.data.message);
      window.location.href = "/home"; 
    } catch (error) {
      alert(error.response?.data?.detail || "Login failed");
    }
  };

  const handleRegister = async () => {
    try {
      await axios.post("http://localhost:8000/users/register/", {
        username,
        email,
        password,
      }, { withCredentials: true });

      alert("Conta criada com sucesso!");
      setRegisterModalOpen(false);
      setLoginModalOpen(true);
    } catch (error) {
      alert(error.response?.data?.detail || "Falha ao criar conta!");
    }
  };

  return (
    <div>
      <h1>Cognizant</h1>

      {/* Modal Login */}
      <Modal
        isOpen={isLoginModalOpen}
        shouldCloseOnOverlayClick={false}
        shouldCloseOnEsc={false}
        className="react-modal-content"
        overlayClassName="react-modal-overlay"
      >
        <h2>Cognizant</h2>
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
        <button onClick={() => { setLoginModalOpen(false); setRegisterModalOpen(true); }}>
          Criar conta
        </button>
      </Modal>

      {/* Modal Register */}
      <Modal
        isOpen={isRegisterModalOpen}
        shouldCloseOnOverlayClick={false}
        shouldCloseOnEsc={false}
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
        <button onClick={() => { setRegisterModalOpen(false); setLoginModalOpen(true); }}>
          Voltar para Login
        </button>
      </Modal>
    </div>
  );
}
