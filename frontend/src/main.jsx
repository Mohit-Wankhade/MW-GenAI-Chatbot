import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";
import { ConversationProvider } from "./context/ConversationContext";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "react-hot-toast";

ReactDOM.createRoot(document.getElementById("root")).render(

    <BrowserRouter>

        <AuthProvider>
            <ConversationProvider>
                
    <App />
    <Toaster
        position="top-right"
        reverseOrder={false}
        toastOptions={{
            duration: 3000,
            style: {
                background: "#2b2d31",
                color: "#fff",
                border: "1px solid #3b3d42",
            },
        }}
    />

            </ConversationProvider>
        </AuthProvider>

    </BrowserRouter>

);