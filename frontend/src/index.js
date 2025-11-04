import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// SERVICE WORKER DESACTIVADO - Causaba errores en producción
// Se usará estrategia de cache HTTP en su lugar
console.log('PWA: Service Worker desactivado para estabilidad en producción');
