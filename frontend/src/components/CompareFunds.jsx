import React, { useState } from "react";
import NavGraph from "./NavGraph.jsx";
import styles from "./CompareFunds.module.css";

export default function CompareFunds() {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedFunds, setSelectedFunds] = useState([]);
  const [fundData, setFundData] = useState({}); // { fundCode: navHistory }

  const colors = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#0088FE", "#00C49F"];

  // Search fund names
  const handleSearch = async (e) => {
    const value = e.target.value;
    setSearchTerm(value);

    if (value.length >= 2) {
      try {
        const response = await fetch(
          `http://localhost:8000/api/funds/search?q=${encodeURIComponent(value)}`
        );
        const data = await response.json();

        const cleanedFunds = data.funds.map((fund) => ({
          ...fund,
          name: fund.name.replace(/^name\s*/i, "").trim(),
        }));

        setSearchResults(cleanedFunds);
        setShowDropdown(true);
      } catch (err) {
        console.error("Search failed:", err);
      }
    } else {
      setSearchResults([]);
      setShowDropdown(false);
    }
  };

  // Add fund from dropdown
  const handleSelectFund = async (fund) => {
    if (!selectedFunds.some((f) => f.code === fund.code)) {
      setSelectedFunds([...selectedFunds, fund]);

      try {
        const response = await fetch(
          `http://localhost:8000/api/funds/nav_history/${fund.code}`
        );
        const data = await response.json();

        const sortedNavHistory = (data.data || []).sort((a, b) => {
          const dateA = new Date(a.date.split("-").reverse().join("-"));
          const dateB = new Date(b.date.split("-").reverse().join("-"));
          return dateA - dateB;
        });

        setFundData((prev) => ({ ...prev, [fund.code]: sortedNavHistory }));
      } catch (err) {
        console.error(err.message);
      }
    }
    setSearchTerm("");
    setShowDropdown(false);
  };

  // Remove selected fund
  const handleRemoveFund = (fundCode) => {
    setSelectedFunds(selectedFunds.filter((f) => f.code !== fundCode));
    setFundData((prev) => {
      const updated = { ...prev };
      delete updated[fundCode];
      return updated;
    });
  };

  // Combine all fund data for a single chart
  const combinedChartData = () => {
    const datesSet = new Set();
    selectedFunds.forEach((fund) => {
      (fundData[fund.code] || []).forEach((item) => datesSet.add(item.date));
    });

    const dates = Array.from(datesSet).sort((a, b) => {
      const dateA = new Date(a.split("-").reverse().join("-"));
      const dateB = new Date(b.split("-").reverse().join("-"));
      return dateA - dateB;
    });

    return dates.map((date) => {
      const entry = { date };
      selectedFunds.forEach((fund) => {
        const navItem = (fundData[fund.code] || []).find((d) => d.date === date);
        entry[fund.code] = navItem ? parseFloat(navItem.nav) : null;
      });
      return entry;
    });
  };

  return (
    <div className={styles.container}>
      <h2>Compare Multiple Funds</h2>

      <input
        type="text"
        placeholder="Search fund name"
        value={searchTerm}
        onChange={handleSearch}
        className={styles.searchInput}
      />

      {showDropdown && searchResults.length > 0 && (
        <ul className={styles.suggestionsList}>
          {searchResults.map((fund) => (
            <li
              key={fund.code}
              className={styles.suggestionItem}
              onClick={() => handleSelectFund(fund)}
            >
              {fund.name} ({fund.code})
            </li>
          ))}
        </ul>
      )}

      {selectedFunds.length > 0 && (
        <div className={styles.selectedFunds}>
          {selectedFunds.map((fund) => (
            <div key={fund.code} className={styles.fundTag}>
              {fund.name}
              <button
                className={styles.removeButton}
                onClick={() => handleRemoveFund(fund.code)}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      {selectedFunds.length > 0 && (
        <div className={styles.graphs}>
          <h3>Comparison Chart</h3>
          <NavGraph
            navHistory={combinedChartData()}
            multiLine={true}
            lineColors={selectedFunds.map((_, idx) => colors[idx % colors.length])}
            fundCodes={selectedFunds.map((f) => f.code)}
          />
        </div>
      )}
    </div>
  );
}
