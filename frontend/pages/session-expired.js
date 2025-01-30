import { useEffect } from "react";
import { useRouter } from "next/router";

function SessionExpired() {
  const router = useRouter();

  // Função para redirecionar após 3 segundos
  useEffect(() => {
    setTimeout(() => {
      router.push("/"); // Redireciona para a página inicial após 3 segundos
    }, 3000);
  }, [router]);

  return (
    <div
      style={{
        position: "fixed", // Fixa a mensagem na tela
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        backgroundColor: "rgba(0, 0, 0, 0.7)", // Fundo escuro para destacar a mensagem
        color: "white",
        display: "flex",
        justifyContent: "center", // Centraliza horizontalmente
        alignItems: "center", // Centraliza verticalmente
        fontSize: "25px",
        zIndex: 1000, // Garante que a mensagem fique sobre outros elementos
      }}
    >
      <p>Faça login para continuar..</p>
    </div>
  );
}

export default SessionExpired;
