import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./MutualFunds.module.css";

export default function MutualFunds() {
  const [funds, setFunds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const fetchFunds = async (pageNum) => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/funds/names?page=${pageNum}`
      );
      if (!response.ok) throw new Error("Failed to fetch funds");
      const data = await response.json();
      // Clean up fund names by removing leading "as" and extra whitespace
      const cleanedFunds = data.funds.map((fund) => ({
        ...fund,
        name: fund.name.replace(/^as\s*/i, "").trim(),
      }));
      setFunds(cleanedFunds);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFunds(1);
  }, []);

  const handleLoadMore = () => {
    setPage((prev) => prev + 1);
    fetchFunds(page + 1);
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
      <div className={styles.fundList}>
        {funds.map((fund, index) => (
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
      <button
        className={styles.loadMoreButton}
        onClick={handleLoadMore}
      >
        Load More Funds
      </button>
    </div>
  );
}
