import { useState } from 'react';
import styles from '../styles/components/UploadFile.module.css';

const CustomFileInput = ({ onFileSelect, resetInput }) => {
  const [files, setFiles] = useState([]);
  const [inputKey, setInputKey] = useState(Date.now());

  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    setFiles(selectedFiles);
    if (onFileSelect) {
      onFileSelect(selectedFiles);
    }
  };

  // Reset input
  const resetFileInput = () => {
    setFiles([]);
    setInputKey(Date.now());
  };


  if (resetInput) {
    resetInput(resetFileInput);
  }

  return (
    <label className={styles.uploadLabel}>
      <img 
        src="https://www.pngplay.com/wp-content/uploads/8/Upload-Icon-Image-Background-PNG-Image.png" // Just a placeholder image for the upload icon, i'm not using 'Public' folder to store images
        alt="Upload" 
        className={styles.uploadIcon} 
      />
      <span>{files.length > 0 ? files.map(f => f.name).join(", ") : "No file selected."}</span>
      <input
        key={inputKey} 
        type="file"
        multiple
        className={styles.hiddenInput}
        onChange={handleFileChange}
      />
    </label>
  );
};

export default CustomFileInput;
