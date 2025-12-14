import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import AdminSweetForm from '../components/AdminSweetForm';
import { createSweet, updateSweet, deleteSweet, restockSweet } from '../services/api';

const AdminPage = ({ sweets, user, onLogout, onRefresh }) => {
  const [editingSweet, setEditingSweet] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (sweetData) => {
    setLoading(true);
    try {
      if (editingSweet) {
        await updateSweet(editingSweet.id, sweetData);
        alert('Sweet updated successfully! ✅');
        setEditingSweet(null);
      } else {
        await createSweet(sweetData);
        alert('Sweet added successfully! ✅');
      }
      await onRefresh();
    } catch (error) {
      console.error('Error:', error);
      alert('Operation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (sweet) => {
    setEditingSweet(sweet);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this sweet?')) {
      setLoading(true);
      try {
        await deleteSweet(id);
        alert('Sweet deleted successfully! 🗑️');
        await onRefresh();
      } catch (error) {
        console.error('Delete error:', error);
        alert('Delete failed. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleRestock = async (id) => {
    const quantity = prompt('Enter quantity to restock:');
    if (quantity && !isNaN(quantity) && parseInt(quantity) > 0) {
      setLoading(true);
      try {
        await restockSweet(id, parseInt(quantity));
        alert('Restock successful! ✅');
        await onRefresh();
      } catch (error) {
        console.error('Restock error:', error);
        alert('Restock failed. Please try again.');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div>
      <Navbar user={user} onLogout={onLogout} />
      
      <div className="container">
        <div style={{ textAlign: 'center', margin: '30px 0' }}>
          <h1>Admin Dashboard 👨‍💼</h1>
          <p style={{ color: '#7f8c8d' }}>Manage your sweet inventory</p>
        </div>

        {loading && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#7f8c8d' }}>
            Processing...
          </div>
        )}

        <div className="admin-container">
          <AdminSweetForm 
            onSubmit={handleSubmit}
            editingSweet={editingSweet}
            onCancelEdit={() => setEditingSweet(null)}
          />

          <div className="admin-sweets">
            <h3>All Sweets ({sweets.length})</h3>
            {sweets.map(sweet => (
              <div key={sweet.id} className="admin-sweet-item">
                <div className="admin-sweet-info">
                  <div style={{ fontSize: '24px', marginBottom: '5px' }}>{sweet.image}</div>
                  <strong>{sweet.name}</strong>
                  <div style={{ color: '#7f8c8d', fontSize: '14px' }}>
                    ₹{sweet.price} | Qty: {sweet.quantity} | {sweet.category}
                  </div>
                  {sweet.description && (
                    <div style={{ color: '#95a5a6', fontSize: '12px', marginTop: '3px' }}>
                      {sweet.description}
                    </div>
                  )}
                </div>
                <div className="admin-sweet-actions">
                  <button 
                    className="btn btn-success btn-sm"
                    onClick={() => handleRestock(sweet.id)}
                    disabled={loading}
                  >
                    Restock
                  </button>
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => handleEdit(sweet)}
                    disabled={loading}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(sweet.id)}
                    disabled={loading}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}

            {sweets.length === 0 && (
              <div style={{ textAlign: 'center', padding: '50px', color: '#7f8c8d' }}>
                <h3>No sweets available. Add your first sweet!</h3>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPage;