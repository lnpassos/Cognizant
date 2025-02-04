import { useState } from "react";
import { FaFolder } from "react-icons/fa";
import { FiX } from "react-icons/fi";
import styles from "../styles/components/FolderItem.module.css";
import Link from "next/link";
import DeleteConfirmationModal from "./DeleteConfirmationModal";

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

      <DeleteConfirmationModal
        isOpen={isModalOpen}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        folderToDelete={folderToDelete}
      />
    </div>
  );
}