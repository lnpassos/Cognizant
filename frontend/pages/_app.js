import { useRouter } from "next/router";
import "../styles/globals.css";

export default function App({ Component, pageProps }) {
  const router = useRouter();
  const isLoginPage = router.pathname === "/";

  return (
    <div className={isLoginPage ? "full-width" : "limited-width"}>
      <Component {...pageProps} />
    </div>
  );
}
