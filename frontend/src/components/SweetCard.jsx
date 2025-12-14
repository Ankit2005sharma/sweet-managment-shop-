import React from 'react';

const SweetCard = ({ sweet, onPurchase, showPurchaseButton = false }) => {
  return (
    <div className="sweet-card">
      <div className="sweet-image">{sweet.image}</div>
      <h3>{sweet.name}</h3>
      {sweet.description && (
        <p style={{ fontSize: '12px', color: '#7f8c8d', margin: '5px 0' }}>
          {sweet.description}
        </p>
      )}
      <div className="sweet-price">₹{sweet.price}</div>
      <div className={`sweet-quantity ${sweet.quantity === 0 ? 'out-of-stock' : ''}`}>
        {sweet.quantity > 0 ? `${sweet.quantity} available` : 'Out of Stock'}
      </div>
      {showPurchaseButton && (
        <button 
          className="btn btn-success"
          disabled={sweet.quantity === 0}
          onClick={() => onPurchase(sweet.id)}
          style={{ 
            width: '100%',
            opacity: sweet.quantity === 0 ? 0.5 : 1,
            cursor: sweet.quantity === 0 ? 'not-allowed' : 'pointer'
          }}
        >
          {sweet.quantity === 0 ? 'Out of Stock' : 'Purchase'}
        </button>
      )}
    </div>
  );
};

export default SweetCard;