import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./MutualFunds.module.css";

const PAGE_SIZE = 20;
const ALPHABETS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

export default function MutualFunds() {
  const [funds, setFunds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [initialLetter, setInitialLetter] = useState("");
  const navigate = useNavigate();

  const fetchFunds = async (pageNum, letter) => {
    setLoading(true);
    try {
      let url = "";
      if (letter) {
        url = `http://localhost:8000/api/funds/names_by_initial?initial=${encodeURIComponent(letter)}`;
      } else {
        url = `http://localhost:8000/api/funds/names?page=${pageNum}`;
      }
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch funds");
      const data = await response.json();

      const fetchedFunds = letter ? data.funds : data.funds;

      const cleanedFunds = fetchedFunds
        .map((f) => ({
          ...f,
          name: f.name.replace(/^as\s*/i, "").trim(),
        }))
        .filter((f) => f.name && !f.name.includes("Name"));

      if (pageNum === 1 || letter) {
        setFunds(cleanedFunds);
      } else {
        setFunds((prev) => [...prev, ...cleanedFunds]);
      }

      setHasMore(!letter ? cleanedFunds.length === PAGE_SIZE : false);
      setError(null);
    } catch (err) {
      setError(err.message);
      setFunds([]);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
    fetchFunds(1, initialLetter);
  }, [initialLetter]);

  const handlePageClick = (pageNum) => {
    if (pageNum < 1) return;
    setPage(pageNum);
    fetchFunds(pageNum, initialLetter);
  };

  const handleInitialLetterClick = (letter) => {
    setInitialLetter(letter);
    setPage(1);
  };

  const clearFilter = () => {
    setInitialLetter("");
    setPage(1);
  };

  const handleFundClick = (fund) => {
    navigate(`/api/funds/details/${fund.code}`, {
      state: { fundName: fund.name },
    });
  };

  if (loading && page === 1)
    return <div className={styles.loading}>Loading...</div>;
  if (error) return <div className={styles.error}>Error: {error}</div>;

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>Available Mutual Funds</h2>

      {/* Initial letter filter */}
      <div className={styles.letterFilter}>
        <button
          className={`${styles.letterButton} ${
            initialLetter === "" ? styles.activeLetter : ""
          }`}
          onClick={clearFilter}
        >
          All
        </button>
        {ALPHABETS.map((letter) => (
          <button
            key={letter}
            className={`${styles.letterButton} ${
              initialLetter === letter ? styles.activeLetter : ""
            }`}
            onClick={() => handleInitialLetterClick(letter)}
          >
            {letter}
          </button>
        ))}
      </div>

      {/* Fund list */}
      <div className={styles.fundList}>
        {funds.map((fund) => (
          <div
            key={fund.code}
            className={styles.fundItem}
            onClick={() => handleFundClick(fund)}
            role="button"
            tabIndex={0}
          >
            {fund.name}
          </div>
        ))}
      </div>

      {/* Pagination Controls (shown only if no initial letter filtering) */}
      {!initialLetter && (
        <div className={styles.pagination}>
          <button
            className={styles.pageButton}
            disabled={page === 1 || loading}
            onClick={() => handlePageClick(page - 1)}
          >
            Previous
          </button>

          <span className={styles.currentPage}>Page {page}</span>

          <button
            className={styles.pageButton}
            disabled={!hasMore || loading}
            onClick={() => handlePageClick(page + 1)}
          >
            Next
          </button>
        </div>
      )}

      <button
        className={styles.loadMoreButton}
        onClick={() => navigate("/api/compare-funds")}
      >
        Compare Funds
      </button>
    </div>
  );
}
