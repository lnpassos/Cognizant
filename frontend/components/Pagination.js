import styles from "../styles/components/Pagination.module.css";

const Pagination = ({ totalItems, itemsPerPage, currentPage, onPageChange }) => {
  const totalPages = Math.max(Math.ceil(totalItems / itemsPerPage), 1);  
  
  const pageNumbers = [];
  for (let i = 1; i <= totalPages; i++) {
    pageNumbers.push(i);
  }

  return (
    <div className={styles.paginationContainer}>
      <button
        className={styles.pageButton}
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        ⬅️
      </button>
      {pageNumbers.map((number) => (
        <button
          key={number}
          className={`${styles.pageButton} ${currentPage === number ? styles.active : ""}`}
          onClick={() => onPageChange(number)}
        >
          {number}
        </button>
      ))}
      <button
        className={styles.pageButton}
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages || totalPages === 0}
      >
        ➡️
      </button>

      <span className={styles.pageCount}>
        {`Page ${currentPage} / ${totalPages}`}
      </span>
    </div>
  );
};

export default Pagination;