import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { loginUser } from '../services/api';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await loginUser(formData);
      onLogin(data.user);
      navigate(data.user.role === 'admin' ? '/admin' : '/user');
    } catch (error) {
      console.error('Login error:', error);
setError(error.response?.data?.error || 'Invalid credentials! Please check your email and password.');
} finally {
setLoading(false);
}
};
const handleChange = (e) => {
setFormData({
...formData,
[e.target.name]: e.target.value
});
};
return (
<div className="form-container">
<h2>Sign In</h2>
{error && (
<div style={{
background: '#ffebee',
color: '#c62828',
padding: '10px',
borderRadius: '6px',
marginBottom: '20px',
textAlign: 'center'
}}>
{error}
</div>
)}
<div>
<div className="form-group">
<label>Email</label>
<input
         type="email"
         name="email"
         value={formData.email}
         onChange={handleChange}
         required
         placeholder="Enter your email"
         disabled={loading}
       />
</div>
    <div className="form-group">
      <label>Password</label>
      <input
        type="password"
        name="password"
        value={formData.password}
        onChange={handleChange}
        required
        placeholder="Enter your password"
        disabled={loading}
      />
    </div>

    <button 
      onClick={handleSubmit} 
      className="btn btn-primary" 
      style={{ width: '100%' }}
      disabled={loading}
    >
      {loading ? 'Logging in...' : 'Login'}
    </button>
  </div>

  <div className="form-footer">
    Don't have an account? <Link to="/register">Register here</Link>
  </div>
</div>
);
};
export default Login;