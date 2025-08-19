import React, { useState, useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import styles from './FundDetail.module.css';
import NavGraph from './NavGraph.jsx'; // Import the NavGraph component

export default function FundDetail() {
  const { fundName: fundCode } = useParams(); // fund code from URL
  const location = useLocation();
  const fundName = location.state?.fundName;
  const [fundDetails, setFundDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [navHistory, setNavHistory] = useState([]);
  const [selectedFrequency, setSelectedFrequency] = useState("weekly"); // default table

  const [avgNavHistory, setAvgNavHistory] = useState([]);


  useEffect(() => {
  const fetchNavHistory = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/funds/nav_history/${fundCode}`);
      if (!response.ok) throw new Error('Failed to fetch NAV history');
      const data = await response.json();

      // Sort by date ascending
      const sortedNavHistory = (data.data || []).sort((a, b) => {
        const dateA = new Date(a.date.split('-').reverse().join('-'));
        const dateB = new Date(b.date.split('-').reverse().join('-'));
        return dateA - dateB;
      });

      setNavHistory(sortedNavHistory);
    } catch (err) {
      setError(err.message);
    }
  };

  fetchNavHistory();
}, [fundCode]);

useEffect(() => {
  const fetchFundDetails = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/funds/details/${fundCode}`);
      if (!response.ok) throw new Error('Failed to fetch fund details');
      const data = await response.json();

      setFundDetails(data); // Only set fund details, do NOT set navHistory
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  fetchFundDetails();
}, [fundCode]);

const getCurrentNav = () => {
  if (navHistory.length === 0) return "N/A";
  // Assuming navHistory is sorted oldest → newest
  return navHistory[navHistory.length - 1].nav;
};
const computeAvgNav = (data, freq) => {
  if (!data || data.length === 0) return [];

  const grouped = {};

  data.forEach(item => {
    const [day, month, year] = item.date.split("-");
    let key;

    if (freq === "weekly") {
      const weekNumber = Math.ceil(parseInt(day) / 7); // simple week of month
      key = `${year}-${month}-W${weekNumber}`;
    } else if (freq === "monthly") {
      key = `${year}-${month}`;
    } else if (freq === "yearly") {
      key = `${year}`;
    } else {
      key = item.date; // daily
    }

    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(parseFloat(item.nav));
  });

  // Compute average NAV for each group
  const result = Object.entries(grouped).map(([key, values]) => ({
    period: key,
    avgNav: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(4),
  }));

  // Sort ascending
  return result.sort((a, b) => new Date(a.period.split("-").reverse().join("-")) - new Date(b.period.split("-").reverse().join("-")));
};

  if (loading) return <div className={styles.loading}>Loading...</div>;
  if (error) return <div className={styles.error}>Error: {error}</div>;
  if (!fundDetails) return <div className={styles.error}>No fund details found</div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.fundName}>{fundName}</h1>
        <div className={styles.currentNav}>
          <span>Current NAV:{getCurrentNav()}</span>
          <span className={styles.navValue}>{fundDetails.current_nav}</span>
        </div>
      </div>

      <div className={styles.grid}>
        {/* Historical NAV Graph */}
        <div className={styles.graphCard}>
          <NavGraph navHistory={navHistory} />
        </div>

        {/* NAV History Table */}
        <div className={styles.historyCard}>
          <h2>NAV History</h2>
          <div className={styles.navOptions}>
            <div className={styles.navOptions}>
  <button onClick={() => setSelectedFrequency("weekly")}>Weekly</button>
  <button onClick={() => setSelectedFrequency("monthly")}>Monthly</button>
  <button onClick={() => setSelectedFrequency("yearly")}>Yearly</button>
</div>



          </div>
          <div className={styles.historyTableWrapper}>
            <table className={styles.historyTable}>
              <thead>
                <tr>
                  <th>Period</th>
                  <th>Average NAV</th>
                </tr>
              </thead>
              <tbody>
                {computeAvgNav(navHistory, selectedFrequency).map((item, index) => (
                  <tr key={index}>
                    <td>{item.period}</td>
                    <td>{item.avgNav}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
