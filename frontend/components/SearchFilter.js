// components/SearchFilter.js
import { useState } from "react";
import { FaSearch } from "react-icons/fa"; // Ícone de busca
import styles from "../styles/components/SearchFilter.module.css";

const SearchFilter = ({ onSearchChange, className }) => {
  const [query, setQuery] = useState("");

  const handleSearchChange = (e) => {
    setQuery(e.target.value);
    onSearchChange(e.target.value); // Chama a função de busca com o valor do input
  };

  return (
    <div className={styles.inputWrapper}>
      <FaSearch className={styles.searchIcon} /> {/* Ícone de busca */}
      <input
        type="text"
        placeholder="Filtrar..."
        value={query}
        onChange={handleSearchChange}
        className={`${className} ${styles.searchFilter}`} // Combina a classe externa com a de filtro
      />
      
    </div>
  );
};

export default SearchFilter;
