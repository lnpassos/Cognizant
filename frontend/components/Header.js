import { useRouter } from "next/router";
import { FaSignOutAlt } from "react-icons/fa"; // Importando ícones
import Link from "next/link"; // Importando Link do Next.js
import styles from "../styles/components/Header.module.css"; 

export default function Header() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      const response = await fetch("http://localhost:8000/logout/", { 
        method: "POST",
        credentials: "include", // Inclui cookies na requisição
      });
  
      if (response.ok) {
        console.log("Logout realizado com sucesso");
        router.push("/");
      } else {
        console.error("Erro ao deslogar:", await response.json());
      }
    } catch (error) {
      console.error("Erro ao deslogar", error);
    }
  };

  return (
    <header className={styles.header}>
      <Link href="/home" className={styles.logo}> {/* Usando Link do Next.js */}
        <img
          src="https://cognizant.scene7.com/is/content/cognizant/COG-Logo-2022-1?fmt=png-alpha"
          alt="Cognizant Logo"
          className={styles["modal-img"]}
        />
      </Link>

      <Link href="/home" className={styles.title}> {/* Usando Link do Next.js */}
        Home
      </Link>

      <button onClick={handleLogout} className={styles.logoutButton}>
        <FaSignOutAlt className={styles.icon} /> Sair
      </button>
    </header>
  );
}
