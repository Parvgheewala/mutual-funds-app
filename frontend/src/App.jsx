import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar.jsx";
import AppRoutes from "./routes/AppRoutes.jsx";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./global.css";
// import "./App.css";

export default function App() {
  const [theme, setTheme] = useState("light");
  

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  return (
    <Router>
      <div className="app" style={{ background: theme === "light" ? "#f9f9f9" : "#121212" }}>
        <Navbar theme={theme} toggleTheme={toggleTheme} />
        <AppRoutes />
      </div>
    </Router>
  );
}