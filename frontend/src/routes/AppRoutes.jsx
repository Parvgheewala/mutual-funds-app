// src/routes/AppRoutes.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import Login from "../components/Login.jsx";
import MutualFunds from "../components/MutualFunds.jsx";
import Questionnaire from "../components/Questionnaire.jsx";
import FundDetail from "../components/FundDetail.jsx";
import CompareFunds from "../components/CompareFunds.jsx";
import SignupForm from "../components/SignupForm.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Landing redirect to login; adjust as needed */}
      <Route path="/" element={<Navigate to="/api/auth" replace />} />

      <Route path="/api/auth" element={<Login />} />
      <Route path="/api/signup" element={<SignupForm />} />

      {/* Core app pages */}
      <Route path="/api/funds" element={<MutualFunds />} />
      <Route path="/api/funds/details/:schemeCode" element={<FundDetail />} />
      <Route path="/api/compare-funds" element={<CompareFunds />} />
      <Route path="/api/questionnaire" element={<Questionnaire />} />
      <Route path="/api/users" element={<SignupForm />} />

      {/* 404 fallback */}
      <Route path="*" element={<div style={{ padding: 24 }}>Not Found</div>} />
    </Routes>
  );
}
