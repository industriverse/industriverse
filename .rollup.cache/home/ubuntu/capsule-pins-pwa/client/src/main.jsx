import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { registerServiceWorker } from "./lib/sw-register";
createRoot(document.getElementById("root")).render(<App />);
// Register service worker for PWA functionality
if (import.meta.env.PROD) {
    registerServiceWorker().then(function (registration) {
        if (registration) {
            console.log('PWA ready: Service worker registered');
        }
    });
}
//# sourceMappingURL=main.jsx.map