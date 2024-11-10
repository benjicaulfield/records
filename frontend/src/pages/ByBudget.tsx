/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/global.css';
import { SellerGroup } from '../types/interfaces';

const ByBudget: React.FC = () => {
  const [budget, setBudget] = useState<number>(0); // Set your budget here
  const [records, setRecords] = useState<SellerGroup[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
      if (budget > 0) {
          setIsLoading(true);
          axios.get(`http://localhost:8000/api/top-records-by-budget/?budget=${budget}`)
              .then(response => {
                  setRecords(response.data);
                  setIsLoading(false);
              })
              .catch(error => {
                  console.error('Error fetching data:', error);
                  setError('Error fetching data');
                  setIsLoading(false);
              });
      }
  }, [budget]);

  return (
    <div>
      <h1>Records by Budget</h1>
      <input
        type="number"
        value={budget}
        onChange={(e) => setBudget(Number(e.target.value))}
        placeholder="Enter your budget"
      />
      <ul>
        {records.map((sellerRecord) => (
          <li key={sellerRecord.seller}>
            <h2>Seller: {sellerRecord.seller}</h2>
            <p>Total Score: {sellerRecord.totalScore}</p>
            <ul>
              {sellerRecord.records.map((record) => (
                <li key={record.id}>
                  {record.title}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
};

export { ByBudget };