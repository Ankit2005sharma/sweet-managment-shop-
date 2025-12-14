import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import UserPage from './pages/UserPage';
import AdminPage from './pages/AdminPage';
import { getAllSweets } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [sweets, setSweets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    fetchSweets();
  }, []);

  const fetchSweets = async () => {
    try {
      setLoading(true);
      const data = await getAllSweets();
      setSweets(data);
    } catch (error) {
      console.error('Error fetching sweets:', error);
      alert('Failed to load sweets. Please check if backend is running on http://localhost:8000');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '24px',
        background: 'linear-gradient(135deg, #fff8e1 0%, #ffe0b2 100%)'
      }}>
        Loading... 🍬
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={<Dashboard sweets={sweets} user={user} onLogout={handleLogout} />} 
        />
        <Route 
          path="/login" 
          element={user ? <Navigate to={user.role === 'admin' ? '/admin' : '/user'} /> : <Login onLogin={handleLogin} />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/" /> : <Register />} 
        />
        <Route 
          path="/user" 
          element={
            user && user.role === 'user' 
              ? <UserPage sweets={sweets} user={user} onLogout={handleLogout} onRefresh={fetchSweets} /> 
              : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/admin" 
          element={
            user && user.role === 'admin' 
              ? <AdminPage sweets={sweets} user={user} onLogout={handleLogout} onRefresh={fetchSweets} /> 
              : <Navigate to="/login" />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;