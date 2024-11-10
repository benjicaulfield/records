import React, { useState, useEffect } from 'react';
import '../css/global.css';

const Home: React.FC = () => {
  const [visitCount, setVisitCount] = useState<number>(0);

  useEffect(() => {
    const storedCount = Number(localStorage.getItem('visitCount') || '0');
    const newCount = storedCount + 1;
    setVisitCount(newCount);
    localStorage.setItem('visitCount', newCount.toString());
  }, []);

  return (
    <div className="container">
      {/* Header with name, visit count, and links */}
      <header className="header">
        <div className="header-left">
          <span>Benjamin Caulfield</span>
          <span className="visit-count">Visits: {visitCount}</span>
        </div>
        <div className="header-links">
          <a href="/dashboard">Dashboard</a> |
          <a href="https://github.com/yourusername" target="_blank" rel="noopener noreferrer">GitHub</a> |
          <a href="https://linkedin.com/in/yourusername" target="_blank" rel="noopener noreferrer">LinkedIn</a> |
          <a href="mailto:your.email@example.com">Gmail</a> |
          <a href="https://bsky.app/profile/yourusername" target="_blank" rel="noopener noreferrer">Bluesky</a>
        </div>
      </header>

      {/* Main Content */}
      <main>
        <p>A legitimate imposter</p>
        <p>BS in CS from NEIU, slowly working towards a Master's in the same</p>
        <p>Focusing on cloud computing, machine learning, NLP, CI/CD</p>
        <p>Python, JavaScript, TypeScript, some Swift, a little Scala</p>
        <p>Django, React, Docker, PostgreSQL, the ML libraries</p>
        <p>I like writing tests. And, cleaning data. Oh, and building APIs.</p>
        <p>Mostly I like collecting long-playing vinyl records</p>
        <p>Record collecting app is built on Django, React in TypeScript, with web scrapers and browser automation tools, 
          a personalized recommendation engine using collaborative filtering and graph clustering, an LLM-powered search engine,
          API integration with Discogs, Ebay, and Spotify, deployed on AWS, Dockerized, and CI/CD pipelines in Jenkins</p>
        <p>Take a peek here: <a href="/dashboard">record monster</a>
        <p></p>
        <p>ASK ME ANYTHING</p>
        </p>
        <div className="cursor">{" > _"}</div>
      </main>
    </div>
  );
};

export { Home };
