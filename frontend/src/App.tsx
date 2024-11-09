import React from 'react';
import './css/global.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BySeller } from "./pages/BySeller";
import { ByBudget } from './pages/ByBudget';
import { SearchForm } from './components/SearchForm';
import { Recommender } from './pages/Recommender';
import { Home } from './pages/Home';


const App: React.FC = () => {  // Annotate App as a functional component
  return (
    <Router>
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path="/budget" element={<ByBudget />} />
        <Route path="/search" element={<SearchForm />} />
        <Route path="/recommender" element={<Recommender />} />
        <Route path="/sellers" element={<BySeller />} />
      </Routes>
    </Router>
    

  );
};

export default App;