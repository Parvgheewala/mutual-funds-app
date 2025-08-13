import React, { useState, useEffect } from "react";
import axios from "axios";
import styles from "./Questionnaire.module.css";

export default function Questionnaire() {
  const [userId] = useState(() => "user_" + Math.floor(Math.random() * 100000));
  const [question, setQuestion] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load first question on mount (hardcoded from QUESTIONS[0] to avoid extra call)
  useEffect(() => {
    setQuestion({
      id: 1,
      question: "What is your primary investment goal?",
      options: [
        "To become financially independent",
        "To secure retirement",
        "To preserve capital",
        "To beat the market",
      ],
    });
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
      } else if (response.data.result) {
        setResult(response.data.result);
        setQuestion(null);
      }
    } catch (err) {
      alert("Error: " + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  }

  if (result) {
    return (
      <div className={styles.card}>
        <h2>Your Investor Profile</h2>
        <p className={styles.resultText}>{result}</p>
      </div>
    );
  }

  if (!question) {
    return (
      <div className={styles.card}>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className={styles.card}>
      <h2>{question.question}</h2>
      <div className={styles.optionsContainer}>
        {question.options.map((opt, idx) => (
          <button
            key={idx}
            disabled={loading}
            onClick={() => submitAnswer(idx)}
            className={styles.optionButton}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}
