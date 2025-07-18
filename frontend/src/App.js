import React, { useState, useEffect } from 'react';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles/globals.css';

// Components
import Layout from './components/Layout';
import AudioUploadEnhanced from './components/enhanced/AudioUploadEnhanced';
import TranscriptionEnhanced from './components/enhanced/TranscriptionEnhanced';
import PostGeneratorEnhanced from './components/enhanced/PostGeneratorEnhanced';
import PostExport from './components/PostExport';
import ErrorBoundary from './components/ErrorBoundary';
import NotificationService from './services/NotificationService';

function App() {
  const [currentStep, setCurrentStep] = useState(1);
  const [workflowState, setWorkflowState] = useState({
    uploadedFile: null,
    transcription: null,
    generatedPosts: {},
    exportReady: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');

  // Load saved workflow state on component mount
  useEffect(() => {
    const savedState = localStorage.getItem('aiSocialGeneratorWorkflow');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setWorkflowState(parsed.workflowState || {});
        setCurrentStep(parsed.currentStep || 1);
      } catch (error) {
        console.error('Failed to load saved workflow state:', error);
      }
    }
  }, []);

  // Save workflow state whenever it changes
  useEffect(() => {
    const stateToSave = {
      workflowState,
      currentStep,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('aiSocialGeneratorWorkflow', JSON.stringify(stateToSave));
  }, [workflowState, currentStep]);

  const handleUploadSuccess = (fileData) => {
    setWorkflowState(prev => ({
      ...prev,
      uploadedFile: fileData,
    }));
    setCurrentStep(2);
    NotificationService.success('Audio file uploaded successfully!');
  };

  const handleUploadError = (error) => {
    console.error('Upload error:', error);
    NotificationService.error('Failed to upload audio file. Please try again.');
  };

  const handleTranscriptionComplete = (transcriptionData) => {
    setWorkflowState(prev => ({
      ...prev,
      transcription: transcriptionData,
    }));
    setCurrentStep(3);
    NotificationService.success('Audio transcription completed successfully!');
  };

  const handlePostsGenerated = (posts) => {
    setWorkflowState(prev => ({
      ...prev,
      generatedPosts: posts,
    }));
    setCurrentStep(4);
    NotificationService.success('Social media posts generated successfully!');
  };

  const handleExportReady = () => {
    setWorkflowState(prev => ({
      ...prev,
      exportReady: true,
    }));
    NotificationService.success('Export completed! You can now start a new session.');
  };

  const handleErrorRecovery = (step) => {
    setCurrentStep(step);
    setIsLoading(false);
    setLoadingMessage('');
    NotificationService.info('Returning to previous step.');
  };

  const resetWorkflow = () => {
    setWorkflowState({
      uploadedFile: null,
      transcription: null,
      generatedPosts: {},
      exportReady: false,
    });
    setCurrentStep(1);
    setIsLoading(false);
    setLoadingMessage('');
    localStorage.removeItem('aiSocialGeneratorWorkflow');
    NotificationService.info('Workflow reset. Starting fresh!');
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                🎤 Upload Your Audio File
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Start by uploading an audio file. We support MP3, WAV, and AAC formats up to 100MB.
              </p>
            </div>
            
            <ErrorBoundary>
              <AudioUploadEnhanced
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />
            </ErrorBoundary>
          </div>
        );

      case 2:
        return workflowState.uploadedFile ? (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                🎯 Audio Transcription
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Converting your audio to text using advanced AI speech recognition.
              </p>
            </div>
            
            <div className="card mb-6">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {workflowState.uploadedFile.filename}
                    </h3>
                    <p className="text-sm text-gray-600">
                      Duration: {Math.floor(workflowState.uploadedFile.duration / 60)}:{(workflowState.uploadedFile.duration % 60).toFixed(0).padStart(2, '0')} • 
                      Size: {(workflowState.uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={() => handleErrorRecovery(1)}
                    className="btn btn-secondary btn-sm"
                  >
                    Change File
                  </button>
                </div>
              </div>
            </div>
            
            <ErrorBoundary>
              <TranscriptionEnhanced
                fileId={workflowState.uploadedFile.file_id}
                onComplete={handleTranscriptionComplete}
                onErrorRecovery={() => handleErrorRecovery(1)}
              />
            </ErrorBoundary>
          </div>
        ) : null;

      case 3:
        return workflowState.transcription ? (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                📱 Generate Social Media Posts
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Create engaging social media content from your transcription using AI.
              </p>
            </div>
            
            <div className="card mb-6">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Transcription Ready
                    </h3>
                    <p className="text-sm text-gray-600">
                      {workflowState.transcription.text?.slice(0, 100)}...
                    </p>
                  </div>
                  <button
                    onClick={() => handleErrorRecovery(2)}
                    className="btn btn-secondary btn-sm"
                  >
                    Edit Transcription
                  </button>
                </div>
              </div>
            </div>
            
            <ErrorBoundary>
              <PostGeneratorEnhanced
                transcriptionId={workflowState.transcription.transcription_id}
                onPostsGenerated={handlePostsGenerated}
                onErrorRecovery={() => handleErrorRecovery(2)}
              />
            </ErrorBoundary>
          </div>
        ) : null;

      case 4:
        return workflowState.generatedPosts && Object.keys(workflowState.generatedPosts).length > 0 ? (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                🎉 Export & Share
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Your social media posts are ready! Export them or share directly to your platforms.
              </p>
            </div>
            
            <ErrorBoundary>
              <PostExport
                posts={workflowState.generatedPosts}
                onExportReady={handleExportReady}
                onErrorRecovery={() => handleErrorRecovery(3)}
              />
            </ErrorBoundary>
            
            <div className="text-center mt-8">
              <button
                onClick={resetWorkflow}
                className="btn btn-primary btn-lg"
              >
                🔄 Start New Session
              </button>
            </div>
          </div>
        ) : null;

      default:
        return null;
    }
  };

  return (
    <ErrorBoundary>
      <Layout
        currentStep={currentStep}
        totalSteps={4}
        isLoading={isLoading}
        loadingMessage={loadingMessage}
        showNavigation={true}
      >
        <div className="max-w-4xl mx-auto">
          {renderStepContent()}
        </div>
      </Layout>
      
      {/* Toast Notification Container */}
      <ToastContainer
        position="top-right"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss={false}
        draggable
        pauseOnHover
        theme="light"
        className="toast-container"
      />
    </ErrorBoundary>
  );
}

export default App;
