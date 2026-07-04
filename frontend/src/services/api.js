import axios from "axios";
import toast from "react-hot-toast";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/";

const API = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    Accept: "application/json",
  },
});

export function getAuthToken() {
  return localStorage.getItem("token");
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem("token", token);
  }
}

export function clearAuthToken() {
  localStorage.removeItem("token");
}

API.interceptors.request.use(
  (config) => {
    const token = getAuthToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

API.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const detail = error?.response?.data?.detail;

    if (status === 401) {
      clearAuthToken();

      if (!window.location.pathname.includes("/login") && window.location.pathname !== "/") {
        toast.error("Session expired. Please login again.");
        window.location.href = "/";
      }
    } else if (status === 413) {
      toast.error("File is too large.");
    } else if (status >= 500) {
      toast.error("Server error. Please try again.");
    } else if (typeof detail === "string" && detail.trim()) {
      toast.error(detail);
    }

    return Promise.reject(error);
  }
);

export default API;