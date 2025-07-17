import React, { useState } from 'react';

const ToneSelector = ({ selectedTone, onToneChange }) => {
  const tones = [
    { value: 'professional', label: 'Professional', description: 'Formal business language' },
    { value: 'casual', label: 'Casual', description: 'Friendly conversational tone' },
    { value: 'witty', label: 'Witty', description: 'Humorous and engaging' },
    { value: 'motivational', label: 'Motivational', description: 'Inspiring and action-oriented' }
  ];

  return (
    <div className="tone-selector">
      <h3>Select a Tone</h3>
      {tones.map((tone) => (
        <label key={tone.value}>
          <input
            type="radio"
            name="tone"
            value={tone.value}
            checked={selectedTone === tone.value}
            onChange={() => onToneChange(tone.value)}
          />
          {tone.label} - {tone.description}
        </label>
      ))}
    </div>
  );
};

export default ToneSelector;
