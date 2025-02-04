import { useEffect } from "react";
import { useRouter } from "next/router";
import Image from "next/image";
import styles from "../styles/NotAuth.module.css"; // Importando o módulo CSS

function SessionExpired() {
  const router = useRouter();

  useEffect(() => {
    setTimeout(() => {
      router.push("/"); // Redireciona para a página inicial após 10 segundos
    }, 5000);
  }, [router]);

  return (
    <div className={styles.sessionExpiredContainer}>
      <div className={styles.imageContainer}>
        <Image
          src="https://cdn-icons-png.flaticon.com/512/7068/7068033.png"
          alt="Session Expired"
          width={150} // Ajustei o tamanho para combinar com o estilo
          height={150}
          className={styles.image}
          priority
        />
      </div>
      <h1 className={styles.title}>Session expired or User not authenticated.</h1>
      <p className={styles.subtitle}>Please log in to continue...</p>
    </div>
  );
}

export default SessionExpired;