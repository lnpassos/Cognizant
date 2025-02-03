import { useState } from "react";
import axios from "axios";
import Modal from "react-modal";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css"; // Importando o CSS para o Toast
import styles from "../styles/Index.module.css";

export default function Home() {
  const [isLoginModalOpen, setLoginModalOpen] = useState(true);
  const [isRegisterModalOpen, setRegisterModalOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const response = await axios.post(
        "http://localhost:8000/login/",
        {
          email,
          password,
        },
        { withCredentials: true }
      );
  
      toast.success(response.data.message); 
      window.location.href = "/home";
    } catch (error) {
      toast.error(error.response?.data?.detail || "Login falhou");
    }
  };
  
  const handleRegister = async () => {
    try {
      await axios.post(
        "http://localhost:8000/register/",
        {
          username,
          email,  
          password,
        },
        { withCredentials: true }
      );
  
      toast.success("Conta criada com sucesso!");
      setRegisterModalOpen(false);
      setLoginModalOpen(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Falha ao criar conta!"); // Exibe um toast de erro
    }
  };

  return (
    <div className={styles["react-modal"]}>
      {/* Modal Login */}
      <Modal
        isOpen={isLoginModalOpen}
        shouldCloseOnOverlayClick={false}
        shouldCloseOnEsc={false}
        className={styles["react-modal-content"]}
        overlayClassName={styles["react-modal-overlay"]}
      >
        <img
          src="https://cognizant.scene7.com/is/content/cognizant/COG-Logo-2022-1?fmt=png-alpha"
          alt="Cognizant Logo"
          className={styles["modal-img"]}
        />
        <input
          type="email" 
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={styles["input-field"]}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles["input-field"]}
        />
        <button className={styles["button-primary"]} onClick={handleLogin}>Sign in</button>
        <button className={styles["button-secondary"]} onClick={() => { setLoginModalOpen(false); setRegisterModalOpen(true); }}>
          Sign up
        </button>
      </Modal>

      {/* Modal Register */}
      <Modal
        isOpen={isRegisterModalOpen}
        shouldCloseOnOverlayClick={false}
        shouldCloseOnEsc={false}
        className={styles["react-modal-content"]}
        overlayClassName={styles["react-modal-overlay"]}
      >
        <img
          src="https://cognizant.scene7.com/is/content/cognizant/COG-Logo-2022-1?fmt=png-alpha"
          alt="Cognizant Logo"
          className={styles["modal-img"]}
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className={styles["input-field"]}
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={styles["input-field"]}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles["input-field"]}
        />
        <button className={styles["button-primary"]} onClick={handleRegister}>Submit</button>
        <button className={styles["button-secondary"]} onClick={() => { setRegisterModalOpen(false); setLoginModalOpen(true); }}>
          Back
        </button>
      </Modal>

      {/* Container for toasts */}
      <ToastContainer />
    </div>
  );
}
