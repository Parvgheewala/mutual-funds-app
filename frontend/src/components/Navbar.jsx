import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Navbar.module.css";
import ThemeToggle from "./ThemeToggle";

export default function Navbar({ theme, toggleTheme }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    const value = e.target.value;
    setSearchTerm(value);

    if (value.length >= 2) {
      try {
        const response = await fetch(
          `http://localhost:8000/api/funds/search?q=${encodeURIComponent(value)}`
        );
        const data = await response.json();
        // Clean up fund names by removing leading "name"
        const cleanedFunds = data.funds.map((fund) => ({
          ...fund,
          name: fund.name.replace(/^name\s*/i, "").trim(),
        }));
        setSearchResults(cleanedFunds);
        setShowDropdown(true);
      } catch (error) {
        console.error("Search failed:", error);
      }
    } else {
      setSearchResults([]);
      setShowDropdown(false);
    }
  };

  const handleFundSelect = (fund) => {
    setShowDropdown(false);
    setSearchTerm("");
    navigate(`/api/funds/details/${fund.code}`, {
      state: { fundName: fund.name },
    });
  };

  // Add home navigation handler
  const handleHomeClick = () => {
    navigate("/api/funds");
  };

  return (
    <nav className={`${styles.navbar} ${theme === "dark" ? styles.dark : ""}`}>
      <div
        className={styles.logo}
        onClick={handleHomeClick}
        role="button"
        tabIndex={0}
      >
        InvestRight
      </div>
      <div className={styles.searchContainer}>
        <input
          type="text"
          className={styles.searchBar}
          placeholder="Search funds..."
          value={searchTerm}
          onChange={handleSearch}
        />
        {showDropdown && searchResults.length > 0 && (
          <div className={styles.searchDropdown}>
            {searchResults.map((fund) => (
              <div
                key={fund.code}
                className={styles.searchItem}
                onClick={() => handleFundSelect(fund)}
              >
                {fund.name}
              </div>
            ))}
          </div>
        )}
      </div>
      <ThemeToggle theme={theme} toggleTheme={toggleTheme} />
    </nav>
  );
}
