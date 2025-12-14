import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import SweetCard from '../components/SweetCard';
import SearchFilter from '../components/SearchFilter';
import { purchaseSweet } from '../services/api';

const UserPage = ({ sweets, user, onLogout, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  const filteredSweets = sweets.filter(sweet =>
    sweet.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handlePurchase = async (id) => {
    setLoading(true);
    try {
      await purchaseSweet(id, 1);
      alert('Purchase successful! 🎉');
      await onRefresh();
    } catch (error) {
      console.error('Purchase error:', error);
      alert(error.response?.data?.error || 'Purchase failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="container">
        <div style={{ textAlign: 'center', margin: '30px 0' }}>
          <h1>Browse Our Sweets 🍬</h1>
          <p style={{ color: '#7f8c8d' }}>Select your favorite sweets and make a purchase</p>
        </div>

        <SearchFilter searchTerm={searchTerm} onSearchChange={setSearchTerm} />

        {loading && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>
            Processing...
          </div>
        )}

        <div className="sweets-grid">
          {filteredSweets.map(sweet => (
            <SweetCard 
              key={sweet.id} 
              sweet={sweet} 
              onPurchase={handlePurchase}
              showPurchaseButton={true}
            />
          ))}
        </div>

        {filteredSweets.length === 0 && (
          <div style={{ textAlign: 'center', padding: '50px', color: '#7f8c8d' }}>
            <h3>No sweets found matching "{searchTerm}"</h3>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserPage;