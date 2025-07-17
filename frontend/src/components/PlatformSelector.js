import React, { useState } from 'react';

const PlatformSelector = ({ selectedPlatforms, onPlatformChange }) => {
  const platforms = [
    { value: 'linkedin', label: 'LinkedIn', limit: '3000 characters', icon: 'linkedin-icon' },
    { value: 'twitter', label: 'Twitter', limit: '280 characters', icon: 'twitter-icon' },
    { value: 'instagram', label: 'Instagram', limit: '2200 characters', icon: 'instagram-icon' }
  ];

  const handlePlatformToggle = (platform) => {
    if (selectedPlatforms.includes(platform)) {
      onPlatformChange(selectedPlatforms.filter(p => p !== platform));
    } else {
      onPlatformChange([...selectedPlatforms, platform]);
    }
  };

  const handleSelectAll = () => {
    if (selectedPlatforms.length === platforms.length) {
      onPlatformChange([]);
    } else {
      onPlatformChange(platforms.map(p => p.value));
    }
  };

  return (
    <div className="platform-selector">
      <h3>Select Platforms</h3>
      <button onClick={handleSelectAll}>
        {selectedPlatforms.length === platforms.length ? 'Deselect All' : 'Select All'}
      </button>
      {platforms.map((platform) => (
        <label key={platform.value}>
          <input
            type="checkbox"
            value={platform.value}
            checked={selectedPlatforms.includes(platform.value)}
            onChange={() => handlePlatformToggle(platform.value)}
          />
          {platform.label} ({platform.limit})
        </label>
      ))}
    </div>
  );
};

export default PlatformSelector;
