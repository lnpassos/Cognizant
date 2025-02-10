import { useRouter } from "next/router";
import { FaSignOutAlt } from "react-icons/fa"; 
import Link from "next/link"; 
import styles from "../styles/components/Header.module.css"; 

export default function Header() {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      const response = await fetch("http://localhost:8000/logout/", { 
        method: "POST",
        credentials: "include", 
      });
  
      if (response.ok) {
        console.log("Logout successful");
        router.push("/"); 
      } else {
        console.error("Error logging out:", await response.json());
      }
    } catch (error) {
      console.error("Error logging out", error);
    }
  };

  return (
    <header className={styles.header}>
      <Link href="/folders" className={styles.logo}>
        <img
          src="https://cognizant.scene7.com/is/content/cognizant/COG-Logo-2022-1?fmt=png-alpha"
          alt="Cognizant Logo"
          className={styles["modal-img"]}
        />
      </Link>

      <Link href="/folders" className={styles.title}>
        Folders
      </Link>

      <button onClick={handleLogout} className={styles.logoutButton}>
        <FaSignOutAlt className={styles.icon} /> Logout
      </button>
    </header>
  );
}
