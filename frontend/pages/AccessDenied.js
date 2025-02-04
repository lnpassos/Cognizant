import Link from "next/link";
import Image from "next/image";
import styles from "../styles/components/AccessDenied.module.css";

const AccessDenied = () => {
  return (
    <div className={styles.container}>
      <div className={styles.imageContainer}>
        <Image
          src="https://cdni.iconscout.com/illustration/premium/thumb/access-denied-illustration-download-in-svg-png-gif-file-formats--not-have-permission-login-empty-states-pack-design-development-illustrations-5913495.png"
          alt="Access Denied"
          width={420}
          height={350}
          className={styles.image}
          priority
        />
      </div>
      <h1 className={styles.text}>
        You do not have permission to access this page!
      </h1>
      <Link href="/home" className={styles.link}>
        Back to Home
      </Link>
    </div>
  );
};

export default AccessDenied;