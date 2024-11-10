import React, { useState, useEffect } from 'react';
import axios from 'axios';

import { Listing } from '../types/interfaces';

export const Recommender: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([]);
  const [keeperIds, setKeeperIds] = useState<number[]>([]);
  const [loserIds, setLoserIds] = useState<number[]>([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/records/recommender')
      .then(response => {
        setListings(response.data);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }, []);

  const handleSelect = (listing_id: number, type: 'keeper' | 'loser') => {
    if (type === 'keeper') {
      setKeeperIds(prev => [...prev, listing_id]);
      setLoserIds(prev => prev.filter(id => id !== listing_id));
    } else {
      setLoserIds(prev => [...prev, listing_id]);
      setKeeperIds(prev => prev.filter(id => id !== listing_id));
    }
  };

  const handleSubmit = () => {
    const payload = {
      keepers: keeperIds,
      losers: loserIds
    };
    axios.post('http://localhost:8000/api/records/recommender/submit-selections', payload)
      .then(response => {
        console.log('Recommendation submitted:', response.data);
        setKeeperIds([]);
        setLoserIds([]);
      })
      .catch(error => {
        console.error('Error submitting selections:', error);
      });
};

return (
  <div>
    <h1>Recommender System</h1>

    {/* Render Records */}
    <div className="listing-list">
      {listings.length > 0 ? (
        listings.map((listing) => (
          <div key={listing.id} className="record-item">
            <h3>{listing.record.artist} - {listing.record.title}</h3>
            <p>Catalog No: {listing.record.catno}</p>
            <p>Condition: {listing.media_condition}</p>
            <p>Price: ${listing.record_price}</p>
            <p>Wants: {listing.record.wants}, Haves: {listing.record.haves}</p>
            <p>Score: {listing.score}</p>
            <div className="selection-buttons">
              <button
                onClick={() => handleSelect(listing.id, 'keeper')}
                disabled={keeperIds.includes(listing.id)}
              >
                Keeper
              </button>
              <button
                onClick={() => handleSelect(listing.id, 'loser')}
                disabled={loserIds.includes(listing.id)}
              >
                Loser
              </button>
            </div>
          </div>
        ))
      ) : (
        <p>Loading records...</p>
      )}
    </div>

    {/* Submit Selections */}
    <button onClick={handleSubmit} disabled={keeperIds.length === 0 && loserIds.length === 0}>
      Submit Selections
    </button>
  </div>
);
};

export default Recommender;