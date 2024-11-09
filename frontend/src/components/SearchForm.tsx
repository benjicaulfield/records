import React, { useState } from 'react';
import axios from 'axios';
import { SearchResult } from '../types';

const SearchForm: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);

  const handleSearch = async () => {
    try {
      const response = await axios.get<SearchResult>('/api/tokenize-records/');
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching search results:', error);
    }
  };

  return (
    <div>
      <h1>Search Records</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter search query"
      />
      <button onClick={handleSearch}>Search</button>
      {results && (
        <div>
        <h2>Search Results</h2>
        <pre>{JSON.stringify(results, null, 2)}</pre>
        <h3>ChatGPT Output</h3>
        <p>{results.chatgpt_output}</p>
      </div>
      )}
    </div>
  );
};

export { SearchForm };