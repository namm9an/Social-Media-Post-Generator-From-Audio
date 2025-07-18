import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import Layout from './Layout';
import AudioUpload from './enhanced/AudioUploadEnhanced';
import TranscriptionView from './enhanced/TranscriptionEnhanced';
import PostGenerator from './enhanced/PostGeneratorEnhanced';
import PostExport from './PostExport';
import NotificationService from '../services/NotificationService';

const WorkflowManager = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [workflowState, setWorkflowState] = useState({
    uploadedFile: null,
    transcription: null,
    generatedPosts: {},
    exportReady: false,
  });
  const history = useHistory();

  useEffect(() => {
    const savedState = JSON.parse(localStorage.getItem('workflowState'));
    if (savedState) {
      setWorkflowState(savedState);
      setCurrentStep(savedState.currentStep || 1);
    }
  }, []);

  // Persist workflow state in localStorage
  useEffect(() => {
    localStorage.setItem('workflowState', JSON.stringify({
      ...workflowState,
      currentStep,
    }));
  }, [workflowState, currentStep]);

  const handleUploadSuccess = (fileData) => {
    setWorkflowState({
      ...workflowState,
      uploadedFile: fileData,
    });
    setCurrentStep(2);
    NotificationService.success('File uploaded successfully!');
  };

  const handleUploadError = (error) => {
    console.error('Upload error:', error);
    NotificationService.error('File upload failed!');
  };

  const handleTranscriptionComplete = (transcriptionData) => {
    setWorkflowState({
      ...workflowState,
      transcription: transcriptionData,
    });
    setCurrentStep(3);
    NotificationService.success('Transcription completed!');
  };

  const handlePostsGenerated = (posts) => {
    setWorkflowState({
      ...workflowState,
      generatedPosts: posts,
    });
    setCurrentStep(4);
    NotificationService.success('Posts generated successfully!');
  };

  const handleExportReady = () => {
    setWorkflowState({
      ...workflowState,
      exportReady: true,
    });
    NotificationService.success('Export is ready!');
  };

  const handleErrorRecovery = (step) => {
    setCurrentStep(step);
    NotificationService.info('Resuming from the last step.');
  };

  const renderStepComponent = () => {
    switch (currentStep) {
      case 1:
        return (
          <AudioUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        );
      case 2:
        return workflowState.uploadedFile ? (
          <TranscriptionView
            fileId={workflowState.uploadedFile.file_id}
            onComplete={handleTranscriptionComplete}
            onErrorRecovery={() => handleErrorRecovery(1)}
          />
        ) : null;
      case 3:
        return workflowState.transcription ? (
          <PostGenerator
            transcriptionId={workflowState.transcription.transcription_id}
            onPostsGenerated={handlePostsGenerated}
            onErrorRecovery={() => handleErrorRecovery(2)}
          />
        ) : null;
      case 4:
        return workflowState.generatedPosts ? (
          <PostExport
            posts={workflowState.generatedPosts}
            onExportReady={handleExportReady}
            onErrorRecovery={() => handleErrorRecovery(3)}
          />
        ) : null;
      default:
        return null;
    }
  };

  return <Layout currentStep={currentStep}>{renderStepComponent()}</Layout>;
};

export default WorkflowManager;

