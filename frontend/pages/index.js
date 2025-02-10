import { useState } from "react";
import { useRouter } from "next/router";
import { toast } from "react-toastify";
import { ClipLoader } from "react-spinners";
import Modal from "react-modal";
import { loginUser, registerUser } from "../services/userService";
import styles from "../styles/Index.module.css";

export default function Home() {
  const [isLoginModalOpen, setLoginModalOpen] = useState(true);
  const [isRegisterModalOpen, setRegisterModalOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    setIsLoading(true);
    try {
      await loginUser(email, password);
      router.push("/folders");
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async () => {
    setIsLoading(true);
    try {
      await registerUser(username, email, password);
      toast.success("Account successfully created!");
      setRegisterModalOpen(false);
      setLoginModalOpen(true);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
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
        <button className={styles["button-primary"]} onClick={handleLogin}>
          {isLoading ? <ClipLoader size={24} color="#ffffff" /> : "Sign in"}
        </button>
        <button
          className={styles["button-secondary"]}
          onClick={() => {
            setLoginModalOpen(false);
            setRegisterModalOpen(true);
          }}
        >
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
        <button className={styles["button-primary"]} onClick={handleRegister}>
          {isLoading ? <ClipLoader size={24} color="#ffffff" /> : "Submit"}
        </button>
        <button
          className={styles["button-secondary"]}
          onClick={() => {
            setRegisterModalOpen(false);
            setLoginModalOpen(true);
          }}
        >
          Back
        </button>
      </Modal>
    </div>
  );
}
