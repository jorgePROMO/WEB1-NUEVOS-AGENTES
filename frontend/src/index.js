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

// Register Service Worker for PWA with auto-update
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then((registration) => {
        console.log('✅ PWA: Service Worker registrado');
        
        // FORZAR actualización inmediata al cargar
        registration.update();
        
        // Chequear actualizaciones cada 30 segundos (más frecuente)
        setInterval(() => {
          registration.update();
        }, 30000);
        
        // Detectar nueva versión disponible
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          console.log('🔄 Nueva versión detectada, actualizando...');
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // Nueva versión instalada, activar inmediatamente
              newWorker.postMessage({ type: 'SKIP_WAITING' });
              
              // Mostrar alert visual al usuario
              console.log('✨ Nueva versión lista');
              alert('🎉 ¡Actualización disponible! La app se recargará automáticamente.');
              
              // Recargar página después de 1 segundo
              setTimeout(() => {
                window.location.reload();
              }, 1000);
            }
          });
        });
      })
      .catch((error) => {
        console.log('❌ PWA: Error al registrar Service Worker', error);
      });
    
    // Escuchar mensaje del service worker
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      console.log('🔄 Service Worker actualizado, recargando...');
      window.location.reload();
    });
  });
}
