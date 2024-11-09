import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <>
      {/* Header */}
      <header className="hero">
        <div className="hero-overlay">
          <h1>Benjamin Caulfield</h1>
          <p>Legitimate Imposter</p>
          <nav className="navbar">
            <Link className="navbar-brand logo" to="/"></Link>
            <ul className="nav-links">
              <li><Link className="nav-link" to="/">Home</Link></li>
              <li><Link className="nav-link" to="/about">About</Link></li>
              <li><Link className="nav-link" to="/graphs">Graphs</Link></li>
              <li><Link className="nav-link" to="/charts">Charts</Link></li>
            </ul>
            <form className="login-form">
              <input type="text" className="form-control" placeholder="Username" />
              <input type="password" className="form-control" placeholder="Password" />
              <button type="submit" className="btn">Login</button>
            </form>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="content-container">
        <div className="box">
          <h2>Welcome to My Myspace-Inspired Page</h2>
          <p>This page brings back the Myspace vibes, styled like it’s 2005.</p>
        </div>
        <div className="box friends">
          <h2>Top Friends</h2>
          <p>Friend 1, Friend 2, Friend 3</p>
        </div>
        <div className="box comments">
          <h2>Comments</h2>
          <p>Leave a comment and let me know you stopped by!</p>
        </div>
      </main>
    </>
  );
};

export { Home };
