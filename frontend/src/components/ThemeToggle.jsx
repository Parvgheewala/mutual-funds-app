import React from "react";
import styles from "./ThemeToggle.module.css";

export default function ThemeToggle({ theme, toggleTheme }) {
  return (
    <button className={styles.toggleBtn} onClick={toggleTheme}>
      {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
    </button>
  );
}
