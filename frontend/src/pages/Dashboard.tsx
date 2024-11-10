import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/global.css';

import { Listing } from '../types/interfaces';

const Dashboard: React.FC = () => {
    const [listings, setListings] = useState<Listing[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        setIsLoading(true);
        axios.get('http://localhost:8000/api/records/dashboard/')
            .then(response => {
                setListings(response.data);
                setIsLoading(false);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                setError(error);
                setIsLoading(false);
            });
    }, []);

    return (
      <div>
        <h1>Dashboard</h1>
        {isLoading ? (
          <p>Loading...</p>
        ) : error ? (
          <p>Error: {error.message}</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Score</th>
                <th>Artist</th>
                <th>Title</th>
                <th>Label</th>
                <th>Year</th>
                <th>Genres</th>
                <th>Styles</th>
                <th>Wants</th>
                <th>Haves</th>
                <th>Media Condition</th>
                <th>Suggested Price</th>
                <th>Record Price</th>
              </tr>
            </thead>
            <tbody>
              {listings.map((listing) => (
                <tr key={listing.id}>
                  <td>{listing.score}</td>
                  <td>{listing.record.artist}</td>
                  <td>{listing.record.title}</td>
                  <td>{listing.record.label}</td>
                  <td>{listing.record.year}</td>
                  <td>{listing.record.genres}</td>
                  <td>{listing.record.styles}</td>
                  <td>{listing.record.wants}</td>
                  <td>{listing.record.haves}</td>
                  <td>{listing.media_condition}</td>
                  <td>{listing.record.suggested_price}</td>
                  <td>{listing.record_price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  };
  
  export { Dashboard };
