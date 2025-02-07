import { useState } from "react";
import { FaSearch } from "react-icons/fa";
import styles from "../styles/components/SearchFilter.module.css";

const SearchFilter = ({ onSearchChange, className }) => {
  const [query, setQuery] = useState("");

  const handleSearchChange = (e) => {
    setQuery(e.target.value);
    onSearchChange(e.target.value);
  };

  return (
    <div className={styles.inputWrapper}>
      <FaSearch className={styles.searchIcon} />
      <input
        type="text"
        placeholder="Filter..."
        value={query}
        onChange={handleSearchChange}
        className={`${className} ${styles.searchFilter}`}
      />
      
    </div>
  );
};

export default SearchFilter;
