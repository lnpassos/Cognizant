// components/SearchFilter.js
import { useState } from "react";

const SearchFilter = ({ onSearchChange, className }) => {
  const [query, setQuery] = useState("");

  const handleSearchChange = (e) => {
    setQuery(e.target.value);
    onSearchChange(e.target.value); // Chama a função de busca com o valor do input
  };

  return (
    <input
      type="text"
      placeholder="Filtrar..."
      value={query}
      onChange={handleSearchChange}
      className={className}
    />
  );
};

export default SearchFilter;
