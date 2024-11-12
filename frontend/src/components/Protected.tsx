import React, { useEffect } from 'react';
import { useQuery } from 'react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

const Protected: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { data, isLoading, isError } = useQuery('user', () =>
    axios.get('/api/user/').then(res => res.data)
  );

  useEffect(() => {
    if (isError) {
      navigate('/');
    } else if (!isLoading && !data) {
      navigate(`/?redirect=${location.pathname}`);
    }
  }, [isLoading, data, isError, navigate, location.pathname]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return <>{children}</>;
};

export { Protected };