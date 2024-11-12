import React, { useState } from 'react';
import axios from 'axios';
import '../css/global.css';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [loginError, setLoginError] = useState('');
  const [registerError, setRegisterError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/login/', { username, password });
      if (response.data.token) {
        navigate('/dashboard');
      }
    } catch (err) {
      setLoginError('Invalid credentials');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/register/', { username, password, email });
      if (response.data.success) {
        navigate('/dashboard');
      }
    } catch (err) {
      setRegisterError('Registration failed. Please check your inputs.');
    }
  };

  return (
    <div className="container">
      <header className="header">
        <div className="header-left">
          <form onSubmit={handleLogin} className="login-form">
            <h3>Login</h3>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Login</button>
            {loginError && <p className="error">{loginError}</p>}
          </form>
          <form onSubmit={handleRegister} className="register-form">
            <h3>Register</h3>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <button type="submit">Register</button>
            {registerError && <p className="error">{registerError}</p>}
          </form>
        </div>
        <div className="header-links">
          <a href="/dashboard">Dashboard</a> |
          <a href="https://github.com/yourusername" target="_blank" rel="noopener noreferrer">GitHub</a> |
          <a href="https://linkedin.com/in/yourusername" target="_blank" rel="noopener noreferrer">LinkedIn</a> |
          <a href="mailto:your.email@example.com">Gmail</a> |
        </div>
      </header>
      <main>
        <p>INTRODUCTORY TEXT ALL ABOUT EVERYTHING</p>
        <p>ASK ME ANYTHING</p>
        <div className="cursor">{" > _"}</div>
      </main>
    </div>
  );
};

export { Home };