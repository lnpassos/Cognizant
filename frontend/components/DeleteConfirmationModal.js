import { IoWarningOutline } from "react-icons/io5";
import styles from "../styles/components/DeleteConfirmationModal.module.css";

export default function DeleteConfirmationModal({
  isOpen,
  onConfirm,
  onCancel,
  folderToDelete,
}) {
  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalDelete}>
        <div className={styles.modalHeader}>
          <span className={styles.modalTitle}>Confirmação</span>
        </div>
        <div className={styles.modalBody}>
          <IoWarningOutline className={styles.warningIcon} />
          <p>
            Tem certeza que deseja excluir o arquivo <b>"{folderToDelete}"</b>?
          </p>
        </div>
        <div className={styles.modalFooter}>
          <button onClick={onConfirm} className={styles.confirmButton}>
            Sim
          </button>
          <button onClick={onCancel} className={styles.cancelButton}>
            Não
          </button>
        </div>
      </div>
    </div>
  );
}