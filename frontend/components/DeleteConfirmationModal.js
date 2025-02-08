import { IoWarningOutline } from "react-icons/io5";
import styles from "../styles/components/DeleteConfirmationModal.module.css";

export default function DeleteConfirmationModal({
  isOpen,
  onConfirm,
  onCancel,
}) {
  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalDelete}>
        <div className={styles.modalHeader}>
          <span className={styles.modalTitle}>Confirmation</span>
        </div>
        <div className={styles.modalBody}>
          <IoWarningOutline className={styles.warningIcon} />
          <p>
            Are you sure you want to delete?
          </p>
        </div>
        <div className={styles.modalFooter}>
          <button onClick={onConfirm} className={styles.confirmButton}>
            Yes
          </button>
          <button onClick={onCancel} className={styles.cancelButton}>
            No
          </button>
        </div>
      </div>
    </div>
  );
}