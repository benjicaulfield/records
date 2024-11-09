import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for navigation
import '../css/global.css';

// Define the Record interface to ensure type safety
export interface Record {
  id: number;
  artist: string;
  title: string;
  format: string;
  seller: string;
  subtitle: string;
  label: string;
  catno: string;
  media_condition: string;
  record_price: number; // Assuming record_price is a number after processing
  wants: number;
  haves: number;
  score: number;
  added: string; // You might want to use a Date type if you're handling dates
  processed: boolean;
}

const BySeller: React.FC = () => {
    const [records, setRecords] = useState<Record[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    const [sortedField, setSortedField] = useState<keyof Record | null>(null);
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc' | null>(null);
    const navigate = useNavigate(); // Initialize useNavigate for navigation

    const handleSort = (field: keyof Record) => {
        if (sortedField === field) {
            // Toggle the sort order
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            // Set the new sort field and default to ascending order
            setSortedField(field);
            setSortOrder('asc');
        }
    };
    

    useEffect(() => {
        if (sortedField && sortOrder) {
            const sortedRecords = [...records].sort((a, b) => {
                if (sortOrder === 'asc') {
                    if (a[sortedField] < b[sortedField]) return -1;
                    if (a[sortedField] > b[sortedField]) return 1;
                } else {
                    if (a[sortedField] > b[sortedField]) return -1;
                    if (a[sortedField] < b[sortedField]) return 1;
                }
                return 0;
            });
            setRecords(sortedRecords);
        }
    }, [sortedField, sortOrder, records]);

    useEffect(() => {
        setIsLoading(true);
        axios.get<Record[]>('http://localhost:8000/api/records/') 
            .then(response => {
                setRecords(response.data);
                setIsLoading(false);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                setError(error); 
                setIsLoading(false);
            });
    }, []);

    const handleRowClick = (record: Record) => {
        navigate(`/record/${record.id}`, { state: { record } }); // Navigate to record detail page
    };

    const groupedRecords = records.reduce((acc, record) => {
      const seller = record.seller;
      if (!acc[seller]) {
          acc[seller] = [];
      }
      acc[seller].push(record);
      return acc;
    }, {} as { [key: string]: Record[] });

    return (
      <div>
          <header>
              <div className="logo">LOGOLOGOLOGO</div>
              <div className="search-container">
                  <form>
                      <input type="text" placeholder="Search..." name="search" />
                      <button type="submit">Search</button>
                  </form>
              </div>
              <ul className="nav-links">
                  <li><a href="/shopping">SHOPPING</a></li>
              </ul>
          </header>
          <div className="container">
              <main>
                  <div className="row profile">
                      <div className="col w-40 left">
                          <div className="stats">
                              <h2>Record Stats</h2>

                              {isLoading && <p>Loading records...</p>}
                              {error && <p>Error: {error.message}</p>}

                              {!isLoading && !error && (
                                  <div>
                                      {Object.keys(groupedRecords).map(seller => (
                                          <div key={seller} className="seller-table">
                                              <h3>{seller}s Top 10 Records</h3>
                                              <table>
                                                  <thead>
                                                      <tr>
                                                          <th className={sortedField === 'artist' ? (sortOrder === 'asc' ? 'asc' : 'desc') : ''} onClick={() => handleSort('artist')}>
                                                              Artist
                                                              {sortedField === 'artist' && sortOrder === 'asc' && <span className="arrow">&#8593;</span>}
                                                              {sortedField === 'artist' && sortOrder === 'desc' && <span className="arrow">&#8595;</span>}
                                                          </th>
                                                          <th className={sortedField === 'title' ? (sortOrder === 'asc' ? 'asc' : 'desc') : ''} onClick={() => handleSort('title')}>
                                                              Title
                                                              {sortedField === 'title' && sortOrder === 'asc' && <span className="arrow">&#8593;</span>}
                                                              {sortedField === 'title' && sortOrder === 'desc' && <span className="arrow">&#8595;</span>}
                                                          </th>
                                                          <th>Condition</th>
                                                          <th>Price</th>
                                                          <th>Wants</th>
                                                          <th>Haves</th>
                                                          <th>Score</th>
                                                      </tr>
                                                  </thead>
                                                  <tbody>
                                                      {groupedRecords[seller].slice(0, 10).map(record => (
                                                          <tr key={record.id} onClick={() => handleRowClick(record)}>
                                                              <td>{record.artist}</td>
                                                              <td>{record.title}</td>
                                                              <td>{record.media_condition}</td>
                                                              <td>{record.record_price}</td>
                                                              <td>{record.wants}</td>
                                                              <td>{record.haves}</td>
                                                              <td>{record.score}</td>
                                                          </tr>
                                                      ))}
                                                  </tbody>
                                              </table>
                                          </div>
                                      ))}
                                  </div>
                              )}
                          </div>
                      </div>
                  </div>
              </main>
          </div>
      </div>
  );
};

export { BySeller };