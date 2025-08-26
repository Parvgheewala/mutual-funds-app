import { useState } from "react";
import styles from "./SignupForm.module.css";

export default function SignupForm() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState({ type: "", text: "" });

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((s) => ({ ...s, [name]: value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMsg({ type: "", text: "" });

    try {
      const res = await fetch("http://localhost:8000/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form), // sends { username, email, password }
      });

      // Try to parse server message; fall back if not JSON
      let data;
      try {
        data = await res.json();
      } catch {
        data = null;
      }

      if (res.ok) {
        setMsg({ type: "success", text: "Account created successfully." });
        setForm({ username: "", email: "", password: "" });
      } else {
        const detail =
          (data && (data.detail || data.message)) ||
          `${res.status} ${res.statusText}`;
        setMsg({ type: "error", text: `Signup failed: ${detail}` });
      }
    } catch (err) {
      setMsg({ type: "error", text: "Could not connect to server." });
    } finally {
      setLoading(false);
    }
  };

  const isDisabled =
    loading ||
    !form.username.trim() ||
    !form.email.trim() ||
    !form.password.trim();

  return (
    <div className={styles["signup-container"]}>
      <form className={styles["signup-form"]} onSubmit={onSubmit} noValidate>
        <h2>Create Account</h2>

        <label htmlFor="username">Username</label>
        <input
          id="username"
          name="username"
          type="text"
          autoComplete="username"
          value={form.username}
          onChange={onChange}
          required
          minLength={1}
          maxLength={50}
          placeholder="johndoe"
        />

        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          value={form.email}
          onChange={onChange}
          required
          maxLength={100}
          placeholder="john@example.com"
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          name="password"
          type="password"
          autoComplete="new-password"
          value={form.password}
          onChange={onChange}
          required
          minLength={6}
          maxLength={255}
          placeholder="••••••••"
        />

        <button type="submit" disabled={isDisabled}>
          {loading ? "Creating..." : "Sign Up"}
        </button>

        {msg.text ? (
          <p
            className={
              msg.type === "error"
                ? `${styles["signup-message"]} ${styles.error}`
                : styles["signup-message"]
            }
            role={msg.type === "error" ? "alert" : undefined}
            aria-live="polite"
          >
            {msg.text}
          </p>
        ) : null}
      </form>
    </div>
  );
}
