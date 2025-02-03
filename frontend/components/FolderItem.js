import { useState } from "react";
import { FaFolder } from "react-icons/fa";
import { FiX } from "react-icons/fi"; 
import { IoWarningOutline } from "react-icons/io5"; 
import styles from "../styles/components/FolderItem.module.css";
import Link from "next/link";

export default function FolderItem({ folder, onDelete }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [folderToDelete, setFolderToDelete] = useState(null);

  const handleDeleteClick = (folderPath) => {
    setFolderToDelete(folderPath);
    setIsModalOpen(true);
  };

  const handleConfirmDelete = () => {
    onDelete(folderToDelete);
    setIsModalOpen(false);
  };

  const handleCancelDelete = () => {
    setIsModalOpen(false);
  };

  return (
    <div className={styles.folderItem} title={folder.path}>
      <Link href={`/folders/${folder.path}`} className={styles.folderLink}>
        <FaFolder className={styles.folderIcon} />
        <span className={styles.folderName}>{folder.path}</span>
      </Link>
      <button
        onClick={() => handleDeleteClick(folder.path)}
        className={styles.deleteButton}
      >
        <FiX className={styles.deleteIcon} />
      </button>

      {isModalOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modalDelete }>
            <div className={styles.modalHeader}>
              <span className={styles.modalTitle}>Confirmação</span>
            </div>
            <div className={styles.modalBody}>
              <IoWarningOutline className={styles.warningIcon} />
              <p>Tem certeza que deseja excluir a pasta <b>"{folderToDelete}"</b>?</p>
            </div>
            <div className={styles.modalFooter}>
              <button onClick={handleConfirmDelete} className={styles.confirmButton}>Sim</button>
              <button onClick={handleCancelDelete} className={styles.cancelButton}>Não</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
