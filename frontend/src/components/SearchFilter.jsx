import React from 'react';

const SearchFilter = ({ searchTerm, onSearchChange }) => {
  return (
    <div className="search-filter">
      <input
        type="text"
        placeholder="🔍 Search for sweets..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
      />
    </div>
  );
};

export default SearchFilter;