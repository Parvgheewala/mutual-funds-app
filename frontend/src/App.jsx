import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar.jsx";
import Login from "./components/Login.jsx";
import MutualFunds from "./components/MutualFunds.jsx";
import Questionnaire from "./components/Questionnaire.jsx";
import FundDetail from "./components/FundDetail";
import "./global.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

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
      <div className="app">
        <Navbar theme={theme} toggleTheme={toggleTheme} />
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/api/funds/*" element={<MutualFunds />} />
          <Route path="/api/questionnaire/*" element={<Questionnaire />} />
          <Route path="/api/auth/*" element={<Login />} />
          <Route path="/api/funds/details/:fundName" element={<FundDetail />} />
        </Routes>
      </div>
    </Router>
  );
}