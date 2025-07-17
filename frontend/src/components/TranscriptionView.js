import React, { useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

const TranscriptionView = ({ fileId, onTranscriptionComplete }) => {
  const [transcribing, setTranscribing] = useState(false);
  const [transcription, setTranscription] = useState(null);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [confidence, setConfidence] = useState(0);

  const startTranscription = async () => {
    if (!fileId) return;

    setTranscribing(true);
    setError(null);

    try {
      const result = await apiClient.startTranscription(fileId);
      
      if (result.success) {
        setTranscription(result.data);
        setEditedText(result.data.text);
        setConfidence(result.data.confidence);
        
        if (onTranscriptionComplete) {
          onTranscriptionComplete(result.data);
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setTranscribing(false);
    }
  };

  const handleEdit = () => {
    setEditMode(true);
    setEditedText(transcription.text);
  };

  const handleSaveEdit = () => {
    if (transcription) {
      setTranscription({
        ...transcription,
        text: editedText
      });
      
      if (onTranscriptionComplete) {
        onTranscriptionComplete({
          ...transcription,
          text: editedText
        });
      }
    }
    setEditMode(false);
  };

  const handleCancelEdit = () => {
    setEditedText(transcription.text);
    setEditMode(false);
  };

  const getCharacterCount = (text) => {
    return text ? text.length : 0;
  };

  const getWordCount = (text) => {
    return text ? text.trim().split(/\s+/).filter(word => word.length > 0).length : 0;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4CAF50'; // Green
    if (confidence >= 0.6) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const getConfidenceText = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="transcription-view">
      <div className="transcription-header">
        <h3>🎯 Audio Transcription</h3>
        
        {!transcription && !transcribing && (
          <button 
            onClick={startTranscription}
            disabled={!fileId}
            className="start-transcription-button"
          >
            Start Transcription
          </button>
        )}
      </div>

      {transcribing && (
        <div className="transcription-loading">
          <div className="loading-spinner"></div>
          <p>Transcribing audio... This may take a moment.</p>
          <div className="loading-tips">
            <p>💡 Tip: Better audio quality results in more accurate transcription</p>
          </div>
        </div>
      )}

      {error && (
        <div className="error-message">
          <h4>❌ Transcription Error</h4>
          <p>{error}</p>
          <button onClick={startTranscription} className="retry-button">
            Retry Transcription
          </button>
        </div>
      )}

      {transcription && (
        <div className="transcription-result">
          <div className="transcription-meta">
            <div className="meta-item">
              <span className="meta-label">Language:</span>
              <span className="meta-value">{transcription.language || 'Unknown'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Confidence:</span>
              <span 
                className="meta-value confidence-score"
                style={{ color: getConfidenceColor(confidence) }}
              >
                {getConfidenceText(confidence)} ({(confidence * 100).toFixed(1)}%)
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Processing Time:</span>
              <span className="meta-value">{transcription.processing_time?.toFixed(2)}s</span>
            </div>
          </div>

          <div className="transcription-content">
            <div className="content-header">
              <h4>📝 Transcribed Text</h4>
              <div className="content-actions">
                {!editMode && (
                  <button onClick={handleEdit} className="edit-button">
                    Edit
                  </button>
                )}
              </div>
            </div>

            {editMode ? (
              <div className="edit-mode">
                <textarea
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  className="edit-textarea"
                  placeholder="Edit transcription..."
                  rows={8}
                />
                <div className="edit-actions">
                  <button onClick={handleSaveEdit} className="save-button">
                    Save Changes
                  </button>
                  <button onClick={handleCancelEdit} className="cancel-button">
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div className="display-mode">
                <div className="transcription-text">
                  {transcription.text || 'No transcription text available'}
                </div>
              </div>
            )}

            <div className="text-statistics">
              <div className="stat-item">
                <span className="stat-label">Characters:</span>
                <span className="stat-value">{getCharacterCount(editMode ? editedText : transcription.text)}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Words:</span>
                <span className="stat-value">{getWordCount(editMode ? editedText : transcription.text)}</span>
              </div>
            </div>
          </div>

          <div className="transcription-actions">
            <button 
              onClick={startTranscription} 
              className="retranscribe-button"
              disabled={transcribing}
            >
              Re-transcribe
            </button>
            <button 
              onClick={() => {
                navigator.clipboard.writeText(transcription.text);
                alert('Transcription copied to clipboard!');
              }}
              className="copy-button"
            >
              Copy Text
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptionView;
