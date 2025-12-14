import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import SweetCard from '../components/SweetCard';

const Dashboard = ({ sweets, user, onLogout }) => {
  const navigate = useNavigate();

  const handlePurchaseClick = () => {
    navigate('/login');
  };

  return (
    <div className="dashboard">
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="hero">
        <h1>Welcome to Our Sweet Shop!</h1>
        <p>Discover the finest traditional and modern sweets</p>
        {!user && (
          <p style={{ color: '#ffebee', marginTop: '10px' }}>
            Please sign in to purchase sweets
          </p>
        )}
      </div>

      {user && user.role === 'admin' && (
        <div className="container">
          <div className="admin-quick-access">
            <h3>⚡ Quick Actions</h3>
            <button 
              className="btn btn-success"
              onClick={() => navigate('/admin')}
              style={{ width: '100%', fontSize: '16px' }}
            >
              ⚙️ Go to Admin Panel (Add/Edit/Delete Sweets)
            </button>
          </div>
        </div>
      )}

      <div className="container">
        <div className="sweets-grid">
          {sweets.map(sweet => (
            <div key={sweet.id}>
              <SweetCard sweet={sweet} />
              {!user && (
                <button 
                  className="btn btn-primary" 
                  onClick={handlePurchaseClick}
                  style={{ width: '100%', marginTop: '10px' }}
                >
                  Sign in to Purchase
                </button>
              )}
            </div>
          ))}
        </div>

        {sweets.length === 0 && (
          <div style={{ textAlign: 'center', padding: '50px', color: '#7f8c8d' }}>
            <h3>No sweets available yet. Admin can add sweets!</h3>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;