import React, { useState, useEffect } from 'react';
import { 
  FiEdit3, 
  FiSave, 
  FiDownload, 
  FiCopy, 
  FiPlay, 
  FiPause,
  FiVolume2,
  FiCheckCircle,
  FiAlertCircle,
  FiRefreshCw
} from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import NotificationService from '../../services/NotificationService';
import { CopyToClipboard } from 'react-copy-to-clipboard';

const TranscriptionEnhanced = ({ 
  fileId, 
  onComplete, 
  onErrorRecovery,
  showControls = true 
}) => {
  const [transcription, setTranscription] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [confidence, setConfidence] = useState(0);
  const [language, setLanguage] = useState('');
  const [processingTime, setProcessingTime] = useState(0);
  const [wordCount, setWordCount] = useState(0);
  const [readingTime, setReadingTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentHighlight, setCurrentHighlight] = useState(-1);

  useEffect(() => {
    if (fileId) {
      startTranscription();
    }
  }, [fileId]);

  useEffect(() => {
    if (transcription?.text) {
      setEditedText(transcription.text);
      const words = transcription.text.trim().split(/\s+/).length;
      setWordCount(words);
      setReadingTime(Math.ceil(words / 200)); // Average reading speed: 200 words per minute
    }
  }, [transcription]);

  const startTranscription = async () => {
    setIsLoading(true);
    setError(null);
    
    const toastId = NotificationService.transcriptionProgress('Starting transcription...');
    
    try {
      const response = await fetch('http://216.48.181.216:5000/api/transcribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_id: fileId }),
      });

      if (!response.ok) {
        throw new Error('Transcription failed');
      }

      const result = await response.json();
      
      setTranscription(result);
      setConfidence(result.confidence || 0);
      setLanguage(result.language || 'Unknown');
      setProcessingTime(result.processing_time || 0);
      
      NotificationService.update(toastId, {
        render: 'Transcription completed successfully!',
        type: 'success',
        isLoading: false,
        autoClose: 3000,
      });
      
      onComplete(result);
    } catch (error) {
      setError(error.message);
      NotificationService.update(toastId, {
        render: 'Transcription failed. Please try again.',
        type: 'error',
        isLoading: false,
        autoClose: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async () => {
    if (editedText.trim() === '') {
      NotificationService.validationError('Text content', 'Transcription cannot be empty');
      return;
    }

    try {
      // Update the transcription with edited text
      const updatedTranscription = {
        ...transcription,
        text: editedText,
        edited: true,
        edited_at: new Date().toISOString(),
      };
      
      setTranscription(updatedTranscription);
      setIsEditing(false);
      
      // Update word count and reading time
      const words = editedText.trim().split(/\s+/).length;
      setWordCount(words);
      setReadingTime(Math.ceil(words / 200));
      
      NotificationService.success('Transcription updated successfully');
      
      // Auto-save to localStorage
      localStorage.setItem(`transcription_${fileId}`, JSON.stringify(updatedTranscription));
      
    } catch (error) {
      NotificationService.error('Failed to save transcription');
    }
  };

  const handleCancel = () => {
    setEditedText(transcription.text);
    setIsEditing(false);
  };

  const handleExport = () => {
    const exportData = {
      transcription: transcription.text,
      confidence: confidence,
      language: language,
      processing_time: processingTime,
      word_count: wordCount,
      reading_time: readingTime,
      exported_at: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription_${fileId}.json`;
    a.click();
    URL.revokeObjectURL(url);

    NotificationService.downloadSuccess('Transcription exported');
  };

  const handleCopy = () => {
    NotificationService.copySuccess('Transcription text');
  };

  const handleRetry = () => {
    startTranscription();
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-100';
    if (confidence >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="card-body text-center py-12">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Transcribing Audio
          </h3>
          <p className="text-gray-600">
            This may take a few minutes depending on the audio length...
          </p>
          <div className="mt-4 max-w-md mx-auto">
            <div className="flex justify-between text-sm text-gray-500 mb-1">
              <span>Processing</span>
              <span>Please wait</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-primary-600 h-2 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card border-red-200"
      >
        <div className="card-body text-center py-12">
          <FiAlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Transcription Failed
          </h3>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={handleRetry}
              className="btn btn-primary flex items-center space-x-2"
            >
              <FiRefreshCw className="w-4 h-4" />
              <span>Retry</span>
            </button>
            <button
              onClick={onErrorRecovery}
              className="btn btn-secondary flex items-center space-x-2"
            >
              <span>Go Back</span>
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  if (!transcription) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Transcription Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body text-center">
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(confidence)}`}>
              <FiCheckCircle className="w-4 h-4 mr-1" />
              {getConfidenceLabel(confidence)}
            </div>
            <p className="text-xs text-gray-500 mt-1">Confidence</p>
            <p className="text-lg font-semibold text-gray-900">{Math.round(confidence * 100)}%</p>
          </div>
        </div>

        <div className="card">
          <div className="card-body text-center">
            <FiVolume2 className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <p className="text-xs text-gray-500">Language</p>
            <p className="text-lg font-semibold text-gray-900">{language}</p>
          </div>
        </div>

        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-purple-600 mb-1">{wordCount}</div>
            <p className="text-xs text-gray-500">Words</p>
            <p className="text-xs text-gray-400">{readingTime} min read</p>
          </div>
        </div>

        <div className="card">
          <div className="card-body text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">{processingTime}s</div>
            <p className="text-xs text-gray-500">Processing Time</p>
          </div>
        </div>
      </div>

      {/* Transcription Content */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <FiVolume2 className="w-5 h-5 mr-2" />
              Transcription Result
            </h3>
            {showControls && (
              <div className="flex items-center space-x-2">
                <CopyToClipboard text={transcription.text} onCopy={handleCopy}>
                  <button className="btn btn-sm btn-ghost flex items-center space-x-1">
                    <FiCopy className="w-4 h-4" />
                    <span>Copy</span>
                  </button>
                </CopyToClipboard>
                <button
                  onClick={handleExport}
                  className="btn btn-sm btn-ghost flex items-center space-x-1"
                >
                  <FiDownload className="w-4 h-4" />
                  <span>Export</span>
                </button>
                <button
                  onClick={isEditing ? handleSave : handleEdit}
                  className="btn btn-sm btn-primary flex items-center space-x-1"
                >
                  {isEditing ? <FiSave className="w-4 h-4" /> : <FiEdit3 className="w-4 h-4" />}
                  <span>{isEditing ? 'Save' : 'Edit'}</span>
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="card-body">
          {isEditing ? (
            <div className="space-y-4">
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                placeholder="Edit your transcription here..."
              />
              <div className="flex justify-end space-x-2">
                <button
                  onClick={handleCancel}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="btn btn-primary flex items-center space-x-1"
                >
                  <FiSave className="w-4 h-4" />
                  <span>Save Changes</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                {transcription.text}
              </p>
              {transcription.edited && (
                <div className="mt-4 text-sm text-gray-500 border-t pt-4">
                  <FiEdit3 className="w-4 h-4 inline mr-1" />
                  Last edited: {new Date(transcription.edited_at).toLocaleString()}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      {showControls && !isEditing && (
        <div className="flex justify-center">
          <button
            onClick={() => onComplete(transcription)}
            className="btn btn-primary btn-lg flex items-center space-x-2"
          >
            <span>Continue to Post Generation</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      )}
    </motion.div>
  );
};

export default TranscriptionEnhanced;
