import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import App from "./App";
import { AuthProvider } from "./context/AuthContext";
import { ConversationProvider } from "./context/ConversationContext";
import "./index.css";

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element with id='root' was not found.");
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ConversationProvider>
          <App />
          <Toaster
            position="top-right"
            reverseOrder={false}
            gutter={10}
            toastOptions={{
              duration: 3000,
              style: {
                background: "#2b2d31",
                color: "#fff",
                border: "1px solid #3b3d42",
              },
              success: {
                duration: 2500,
              },
              error: {
                duration: 4000,
              },
            }}
          />
        </ConversationProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);