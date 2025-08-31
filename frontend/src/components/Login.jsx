import React, { useState } from "react";
import styles from "./Login.module.css";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
  e.preventDefault();
  try {
    const res = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier: username || email , password }), // or { identifier: username } if backend changed
    });

    if (!res.ok) {
      alert("Invalid credentials");
      return;
    }

    const data = await res.json();
    // Save token and user
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));

    // Navigate to a frontend route, not the API
    navigate("/api/funds"); // ensure this route exists in React Router
  } catch (err) {
    alert("Login failed");
  }
};


  return (
    <div className={styles.loginContainer}>
      <div className={styles.card}>
        <h2 className={styles.title}>Welcome Back</h2>
        <p className={styles.subtitle}>Access your mutual fund dashboard</p>
        <form className={styles.loginForm} onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">Login</button>
        </form>
        <div className={styles.links}>
          <a href="#">Forgot Password?</a> | <Link to="/api/users">Create Account</Link>
        </div>
      </div>
    </div>
  );
}
