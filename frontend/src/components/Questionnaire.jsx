import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "./Questionnaire.module.css";
import { useNavigate } from "react-router-dom";


export default function Questionnaire() {
  const [userId] = useState(() => "user_" + Math.floor(Math.random() * 100000));
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [question, setQuestion] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Load all questions on mount for progress calculation
  useEffect(() => {
    async function fetchQuestions() {
      try {
        const response = await axios.get("http://localhost:8000/api/questionnaire/questions");
        if (response.data?.questions?.length > 0) {
          setQuestions(response.data.questions);
          setCurrentIndex(0);
          setQuestion(response.data.questions[0]);
        }
      } catch (err) {
        alert("Error fetching questions: " + err.message);
      }
    }
    fetchQuestions();
  }, []);

  async function submitAnswer(answerIndex) {
    setLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/questionnaire/submit/${userId}`,
        {
          question_id: question.id,
          answer_index: answerIndex,
        }
      );

      if (response.data.next_question) {
        setQuestion(response.data.next_question);
        // Update current index based on question id  
        const nextIdx = questions.findIndex(q => q.id === response.data.next_question.id);
        if (nextIdx !== -1) setCurrentIndex(nextIdx);
      } else if (response.data.result) {
        setResult(response.data.result);
        setQuestion(null);
      }
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  }

  // Show final result
  if (result) {
  return (
    <div className={styles.card}>
      <h2 className={styles.title}>Your Investor Profile</h2>
      <p className={styles.resultText}>{result}</p>
      <button
        className={styles.optionButton}
        style={{ marginTop: "2rem" }}
        onClick={() => navigate("/api/funds/")}
      >
        View Mutual Funds
      </button>
    </div>
  );
}

  // Loading / no question state
  if (!question) {
    return (
      <div className={styles.card}>
        <p className={styles.loadingText}>Loading questions...</p>
      </div>
    );
  }

  // Question number + total for progress
  const progressText = questions.length
    ? `Question ${currentIndex + 1} of ${questions.length}`
    : "";

  return (
    <div className={styles.card}>
      {progressText && <div className={styles.progress}>{progressText}</div>}

      <h2 className={styles.title}>{question.question}</h2>

      <div className={styles.optionsContainer}>
        {question.options.map((opt, idx) => (
          <button
            key={idx}
            disabled={loading}
            onClick={() => submitAnswer(idx)}
            className={styles.optionButton}
          >
            {opt.text || opt}
          </button>
        ))}
      </div>

      {loading && <div className={styles.loadingOverlay}>Submitting answer...</div>}
    </div>
  );
}
