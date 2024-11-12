import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import './css/global.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BySeller }  from "./pages/BySeller";
import { ByBudget } from './pages/ByBudget';
import { SearchForm } from './components/SearchForm';
import { Recommender } from './pages/Recommender';
import { Home } from './pages/Home';
import { Dashboard } from './pages/Dashboard';
import { Protected } from './components/Protected';

const queryClient = new QueryClient();  

const App: React.FC = () => {  // Annotate App as a functional component
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path='/' element={<Home />} />
          <Route path='/dashboard' element={<Protected><Dashboard /></Protected>} />
          <Route path="/budget" element={<ByBudget />} />
          <Route path="/search" element={<SearchForm />} />
          <Route path="/recommender" element={<Recommender />} />
          <Route path="/sellers" element={<BySeller />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
};

export default App;