import '../styles/globals.css';
import '../styles/modal.css';   // Seu arquivo modal.css

export default function App({ Component, pageProps }) {
  return (
    <>
      {/* O SessionHandler será executado em todas as páginas */}

      <Component {...pageProps} />
    </>
  );
}
