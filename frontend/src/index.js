import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  // StrictMode DESACTIVADO temporalmente - causaba doble-render del acordeón
  // TODO: Reimplementar con useCallback cuando sea estable
  <App />
);

// FORCE UNREGISTER ALL SERVICE WORKERS
// Esto limpiará Service Workers de dispositivos que ya los tienen instalados
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(registrations) {
    for(let registration of registrations) {
      registration.unregister().then(function(success) {
        if (success) {
          console.log('✅ Service Worker desinstalado correctamente');
        }
      });
    }
  }).catch(function(err) {
    console.log('Error desinstalando Service Workers:', err);
  });
  
  // También limpiar todos los caches
  if ('caches' in window) {
    caches.keys().then(function(names) {
      for (let name of names) {
        caches.delete(name);
        console.log('✅ Cache eliminado:', name);
      }
    });
  }
}

console.log('🚀 App cargada - Service Workers desactivados permanentemente');

