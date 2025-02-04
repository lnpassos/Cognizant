import { useState } from 'react';
import styles from '../styles/components/UploadFile.module.css';

const CustomFileInput = ({ onFileSelect, resetInput }) => {
  const [files, setFiles] = useState([]);
  const [inputKey, setInputKey] = useState(Date.now()); // Estado para resetar input

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
    if (onFileSelect) {
      onFileSelect(selectedFiles);
    }
  };

  // Função para resetar o input
  const resetFileInput = () => {
    setFiles([]);
    setInputKey(Date.now()); // Muda a key do input, forçando re-render
  };

  // Permite que o componente pai possa resetar o input
  if (resetInput) {
    resetInput(resetFileInput);
  }

  return (
    <label className={styles.uploadLabel}>
      <img 
        src="https://www.pngplay.com/wp-content/uploads/8/Upload-Icon-Image-Background-PNG-Image.png" 
        alt="Upload" 
        className={styles.uploadIcon} 
      />
      <span>{files.length > 0 ? files.map(f => f.name).join(", ") : "No file selected."}</span>
      <input
        key={inputKey} // Isso força a re-renderização ao resetar
        type="file"
        multiple
        className={styles.hiddenInput}
        onChange={handleFileChange}
      />
    </label>
  );
};

export default CustomFileInput;
