import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import apiClient from '../services/apiClient';

const AudioUpload = ({ onUploadSuccess, onUploadError }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [validationErrors, setValidationErrors] = useState([]);
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setValidationErrors([]);
    setUploadedFile(null);

    // Validate file
    const validation = apiClient.validateFile(file);
    if (!validation.valid) {
      setValidationErrors(validation.errors);
      if (onUploadError) {
        onUploadError(validation.errors);
      }
      return;
    }

    // Start upload
    setUploading(true);
    setUploadProgress(0);

    try {
      const result = await apiClient.uploadAudio(file);
      
      if (result.success) {
        setUploadedFile({
          ...result.data,
          originalFile: file
        });
        
        if (onUploadSuccess) {
          onUploadSuccess(result.data);
        }
      } else {
        setValidationErrors(result.errors || [result.error]);
        if (onUploadError) {
          onUploadError(result.errors || [result.error]);
        }
      }
    } catch (error) {
      setValidationErrors([error.message]);
      if (onUploadError) {
        onUploadError([error.message]);
      }
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [onUploadSuccess, onUploadError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.ogg', '.flac']
    },
    maxFiles: 1,
    disabled: uploading
  });

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
      onDrop(files);
    }
  };

  const clearFile = () => {
    setUploadedFile(null);
    setValidationErrors([]);
    setUploadProgress(0);
  };

  return (
    <div className="audio-upload-container">
      <div className="upload-section">
        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="dropzone-content">
            {uploading ? (
              <div className="upload-progress">
                <div className="spinner"></div>
                <p>Uploading audio file...</p>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            ) : isDragActive ? (
              <div className="drag-active">
                <p>🎵 Drop your audio file here...</p>
              </div>
            ) : (
              <div className="drag-inactive">
                <p>🎤 Drag and drop an audio file here, or click to select</p>
                <p className="supported-formats">
                  Supported formats: MP3, WAV, M4A, OGG, FLAC
                </p>
                <p className="size-limit">
                  Maximum file size: {process.env.REACT_APP_MAX_FILE_SIZE || 50}MB
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Alternative file input for browsers that don't support drag and drop */}
        <div className="file-input-section">
          <label htmlFor="audio-file-input" className="file-input-label">
            Or choose file manually:
          </label>
          <input
            id="audio-file-input"
            type="file"
            accept=".mp3,.wav,.m4a,.ogg,.flac"
            onChange={handleFileSelect}
            disabled={uploading}
            className="file-input"
          />
        </div>
      </div>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="error-messages">
          <h4>❌ Upload Errors:</h4>
          <ul>
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Upload Success */}
      {uploadedFile && (
        <div className="upload-success">
          <h4>✅ Upload Successful!</h4>
          <div className="file-info">
            <p><strong>File:</strong> {uploadedFile.filename}</p>
            <p><strong>Size:</strong> {apiClient.formatFileSize(uploadedFile.size)}</p>
            <p><strong>Duration:</strong> {apiClient.formatDuration(uploadedFile.duration)}</p>
            <p><strong>Format:</strong> {uploadedFile.format.toUpperCase()}</p>
          </div>
          <button onClick={clearFile} className="clear-button">
            Upload Another File
          </button>
        </div>
      )}
    </div>
  );
};

export default AudioUpload;
