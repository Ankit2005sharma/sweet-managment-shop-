import React, { useState, useEffect } from 'react';

const AdminSweetForm = ({ onSubmit, editingSweet, onCancelEdit }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    quantity: '',
    category: 'traditional',
    image: '🍬'
  });

  useEffect(() => {
    if (editingSweet) {
      setFormData({
        name: editingSweet.name,
        description: editingSweet.description || '',
        price: editingSweet.price,
        quantity: editingSweet.quantity,
        category: editingSweet.category,
        image: editingSweet.image
      });
    }
  }, [editingSweet]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      price: parseFloat(formData.price),
      quantity: parseInt(formData.quantity)
    });
    setFormData({ 
      name: '', 
      description: '',
      price: '', 
      quantity: '', 
      category: 'traditional',
      image: '🍬' 
    });
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="admin-form">
      <h3>{editingSweet ? 'Edit Sweet' : 'Add New Sweet'}</h3>
      
      <div className="form-group">
        <label>Sweet Name</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label>Description</label>
        <input
          type="text"
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Optional"
        />
      </div>

      <div className="form-group">
        <label>Price (₹)</label>
        <input
          type="number"
          name="price"
          value={formData.price}
          onChange={handleChange}
          required
          min="0"
          step="0.01"
        />
      </div>

      <div className="form-group">
        <label>Quantity</label>
        <input
          type="number"
          name="quantity"
          value={formData.quantity}
          onChange={handleChange}
          required
          min="0"
        />
      </div>

      <div className="form-group">
        <label>Category</label>
        <select
          name="category"
          value={formData.category}
          onChange={handleChange}
        >
          <option value="traditional">Traditional</option>
          <option value="modern">Modern</option>
          <option value="festival">Festival Special</option>
          <option value="premium">Premium</option>
        </select>
      </div>

      <div className="form-group">
        <label>Emoji</label>
        <input
          type="text"
          name="image"
          value={formData.image}
          onChange={handleChange}
          maxLength="2"
        />
      </div>

      <button 
        onClick={handleSubmit}
        className="btn btn-success" 
        style={{ width: '100%', marginBottom: '10px' }}
      >
        {editingSweet ? 'Update Sweet' : 'Add Sweet'}
      </button>

      {editingSweet && (
        <button 
          onClick={onCancelEdit} 
          className="btn btn-secondary" 
          style={{ width: '100%' }}
        >
          Cancel
        </button>
      )}
    </div>
  );
};

export default AdminSweetForm;