import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { clearAuthToken, getAuthToken, setAuthToken } from "../services/api";

const AuthContext = createContext(null);

const USERNAME_STORAGE_KEY = "username";

function getStoredUsername() {
  return localStorage.getItem(USERNAME_STORAGE_KEY);
}

function setStoredUsername(username) {
  if (username) {
    localStorage.setItem(USERNAME_STORAGE_KEY, username);
  }
}

function clearStoredUsername() {
  localStorage.removeItem(USERNAME_STORAGE_KEY);
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => getAuthToken());
  const [username, setUsername] = useState(() => getStoredUsername());
  const [isAuthReady, setIsAuthReady] = useState(false);

  useEffect(() => {
    setIsAuthReady(true);
  }, []);

  const login = useCallback((jwt, usernameValue) => {
    if (!jwt) {
      throw new Error("JWT token is required for login.");
    }

    setAuthToken(jwt);
    setToken(jwt);

    if (usernameValue) {
      setStoredUsername(usernameValue);
      setUsername(usernameValue);
    }
  }, []);

  const logout = useCallback(() => {
    clearAuthToken();
    clearStoredUsername();

    setToken(null);
    setUsername(null);
  }, []);

  const updateUsername = useCallback((usernameValue) => {
    if (!usernameValue) {
      clearStoredUsername();
      setUsername(null);
      return;
    }

    setStoredUsername(usernameValue);
    setUsername(usernameValue);
  }, []);

  const value = useMemo(
    () => ({
      token,
      username,
      isAuthenticated: Boolean(token),
      isAuthReady,
      login,
      logout,
      updateUsername,
    }),
    [token, username, isAuthReady, login, logout, updateUsername]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }

  return context;
}