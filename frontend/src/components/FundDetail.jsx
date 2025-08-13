import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import styles from './FundDetail.module.css';

export default function FundDetail() {
  const { fundName: fundCode } = useParams(); // This is now the fund code
  const location = useLocation();
  const fundName = location.state?.fundName;
  const [fundDetails, setFundDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [navHistory, setNavHistory] = useState([]);

  useEffect(() => {
    const fetchFundDetails = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/funds/details/${fundCode}`);
        if (!response.ok) throw new Error('Failed to fetch fund details');
        const data = await response.json();
        setFundDetails(data);
        setNavHistory(data.nav_history || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFundDetails();
  }, [fundCode]);

  if (loading) return <div className={styles.loading}>Loading...</div>;
  if (error) return <div className={styles.error}>Error: {error}</div>;
  if (!fundDetails) return <div className={styles.error}>No fund details found</div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.fundName}>{fundName}</h1>
        <div className={styles.currentNav}>
          <span>Current NAV:</span>
          <span className={styles.navValue}>{fundDetails.current_nav}</span>
        </div>
      </div>

      <div className={styles.grid}>
        {/* Historical NAV Graph */}
        <div className={styles.graphCard}>
          <h2>Historical NAV</h2>
          {/* Add graph component here */}
        </div>

        {/* NAV History Table */}
        <div className={styles.historyCard}>
          <h2>NAV History</h2>
          <div className={styles.navOptions}>
            <button>Weekly</button>
            <button>Monthly</button>
            <button>Yearly</button>
          </div>
          <div className={styles.historyTable}>
            {/* Add table component here */}
          </div>
        </div>
      </div>
    </div>
  );
}