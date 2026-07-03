import { createContext, useContext, useState } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {

    const [token, setToken] = useState(
        localStorage.getItem("token")
    );
    const [username, setUsername] = useState(
    localStorage.getItem("username")
    );

    const login = (jwt, username) => {

    localStorage.setItem("token", jwt);
    localStorage.setItem("username", username);

    setToken(jwt);
    setUsername(username);

};

    const logout = () => {

        localStorage.removeItem("token");
        localStorage.removeItem("username");
        setToken(null);
        setUsername(null);
    };
    

    return (

        <AuthContext.Provider
            value={{
                token,
                login,
                username,
                logout
            }}
        
        >
            {children}
        </AuthContext.Provider>

    );
}

export function useAuth() {
    return useContext(AuthContext);
}