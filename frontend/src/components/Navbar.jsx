import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" style={{ textDecoration: 'none' }}>
          <div className="navbar-brand">Sweet Shop</div>
        </Link>
        <div className="navbar-actions">
          {user ? (
            <>
              <div className="user-info">
                <span>👤 {user.name}</span>
                <span style={{ 
                  background: user.role === 'admin' ? '#e74c3c' : '#3498db',
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '12px'
                }}>
                  {user.role}
                </span>
              </div>
              
              {user.role === 'admin' && (
                <Link to="/admin">
                  <button className="btn btn-success">
                    ⚙️ Admin Panel
                  </button>
                </Link>
              )}

              {user.role === 'user' && (
                <Link to="/user">
                  <button className="btn btn-primary">
                    🛒 My Shopping
                  </button>
                </Link>
              )}

              <button onClick={handleLogout} className="btn btn-secondary">
                Logout
              </button>
            </>
          ) : (
            <Link to="/login">
              <button className="btn btn-primary">Sign In</button>
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;