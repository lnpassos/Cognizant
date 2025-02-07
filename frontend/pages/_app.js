import { useRouter } from "next/router";
import "../styles/globals.css";
import ChatBot from "../components/ChatBot";
import { ToastContainer } from "react-toastify"; 
import "react-toastify/dist/ReactToastify.css"; 

export default function App({ Component, pageProps }) {
  const router = useRouter();
  const isLoginPage = router.pathname === "/";

  return (
    <div className={isLoginPage ? "full-width" : "limited-width"}>
      <Component {...pageProps} />
      <ChatBot />
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  );
}