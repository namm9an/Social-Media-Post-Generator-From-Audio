import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiAlertCircle, FiFile } from 'react-icons/fi';
import NotificationService from '../../services/NotificationService';

const AudioUploadEnhanced = ({ onUploadSuccess, onUploadError }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = (acceptedFiles) => {
    setFiles(
      acceptedFiles.map((file) =>
        Object.assign(file, {
          preview: URL.createObjectURL(file),
        })
      )
    );
  };

  const uploadFile = async (file) => {
    setUploading(true);
    
    const toastId = NotificationService.uploadProgress(file.name, 0);
    
    try {
      const data = new FormData();
      data.append('file', file);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await fetch('http://localhost:5000/api/upload', {
        method: 'POST',
        body: data,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Upload failed');
      }
      
      const result = await response.json();
      
      NotificationService.update(toastId, {
        render: 'Upload completed successfully!',
        type: 'success',
        isLoading: false,
        autoClose: 3000,
      });
      
      onUploadSuccess(result);
      
    } catch (error) {
      console.error('Upload error:', error);
      
      NotificationService.update(toastId, {
        render: `Upload failed: ${error.message}`,
        type: 'error',
        isLoading: false,
        autoClose: 5000,
      });
      
      onUploadError(error);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleUploadClick = () => {
    if (!files.length) return;
    uploadFile(files[0]);
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: 'audio/*',
    maxFiles: 1,
  });

  return (
    <div className="audio-upload">
      <div
        {...getRootProps({
          className:
            'dropzone flex flex-col items-center justify-center bg-gray-100 border border-dashed border-gray-300 rounded-lg p-8 cursor-pointer hover:shadow-md transition-shadow',
        })}
      >
        <input {...getInputProps()} />
        <p className="text-gray-600">
          Drag & drop audio file here, or click to select file
        </p>
        <FiUpload className="text-primary-600 w-12 h-12 mt-3" />
        <em className="text-xs text-gray-400">
          (Only *.wav, *.mp3, *.aac files will be accepted)
        </em>
      </div>

      {files.length > 0 && (
        <div className="file-preview mt-4">
          {files.map((file) => (
            <div
              key={file.path}
              className="p-4 bg-white shadow-md rounded-lg mb-4 flex items-center justify-between"
            >
              <div className="flex items-center space-x-3">
                <FiFile className="w-6 h-6 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {file.path}
                  </p>
                  <p className="text-xs text-gray-600">
                    {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              </div>
              <button
                onClick={handleUploadClick}
                disabled={uploading}
                className="btn-primary flex items-center space-x-1"
              >
                <FiUpload />
                <span>{uploading ? 'Uploading...' : 'Upload'}</span>
              </button>
            </div>
          ))}
        </div>
      )}

      {uploading && (
        <div className="progress-bar mt-4">
          <div
            className="progress-fill bg-primary-600 h-2.5 rounded-full"
            style={{ width: `${uploadProgress}%` }}
          />
        </div>
      )}

      {!files.length && !uploading && (
        <div className="mt-4 text-center text-red-600 bg-red-100 p-3 rounded-lg">
          <FiAlertCircle className="inline-block mr-2 align-middle" />
          <span className="align-middle">
            Please select a valid audio file to upload.
          </span>
        </div>
      )}
    </div>
  );
};

export default AudioUploadEnhanced;

