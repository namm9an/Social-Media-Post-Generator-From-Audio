import React, { useState } from 'react';
import './App.css';
import AudioUpload from './components/AudioUpload';
import TranscriptionView from './components/TranscriptionView';
import PostGenerator from './components/PostGenerator';
import ErrorBoundary from './components/ErrorBoundary';
import Posts from './Posts';

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [transcription, setTranscription] = useState(null);
  const [generatedPosts, setGeneratedPosts] = useState({});
  const [currentStep, setCurrentStep] = useState('upload'); // 'upload', 'transcribe', 'generate'

  const handleUploadSuccess = (fileData) => {
    setUploadedFile(fileData);
    setCurrentStep('transcribe');
  };

  const handleUploadError = (errors) => {
    console.error('Upload errors:', errors);
  };

  const handleTranscriptionComplete = (transcriptionData) => {
    setTranscription(transcriptionData);
    setCurrentStep('generate');
  };

  const handlePostsGenerated = (posts) => {
    setGeneratedPosts(posts);
  };

  const resetApp = () => {
    setUploadedFile(null);
    setTranscription(null);
    setGeneratedPosts({});
    setCurrentStep('upload');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎤 AI Social Media Post Generator</h1>
        <p>Upload audio, transcribe with Whisper, generate social media posts!</p>
        
        {/* Progress indicator */}
        <div className="progress-steps">
          <div className={`step ${currentStep === 'upload' ? 'active' : uploadedFile ? 'completed' : ''}`}>
            <span className="step-number">1</span>
            <span className="step-label">Upload Audio</span>
          </div>
          <div className={`step ${currentStep === 'transcribe' ? 'active' : transcription ? 'completed' : ''}`}>
            <span className="step-number">2</span>
            <span className="step-label">Transcribe</span>
          </div>
          <div className={`step ${currentStep === 'generate' ? 'active' : Object.keys(generatedPosts).length > 0 ? 'completed' : ''}`}>
            <span className="step-number">3</span>
            <span className="step-label">Generate Posts</span>
          </div>
        </div>
      </header>
      
      <main>
        {/* Step 1: Audio Upload */}
        {currentStep === 'upload' && (
          <section className="upload-section">
            <h2>📤 Step 1: Upload Audio File</h2>
            <AudioUpload 
              onUploadSuccess={handleUploadSuccess}
              onUploadError={handleUploadError}
            />
          </section>
        )}
        
        {/* Step 2: Transcription */}
        {currentStep === 'transcribe' && uploadedFile && (
          <section className="transcription-section">
            <h2>🎯 Step 2: Transcribe Audio</h2>
            <div className="file-info">
              <p><strong>File:</strong> {uploadedFile.filename}</p>
              <p><strong>Duration:</strong> {Math.floor(uploadedFile.duration / 60)}:{(uploadedFile.duration % 60).toFixed(0).padStart(2, '0')}</p>
            </div>
            <TranscriptionView 
              fileId={uploadedFile.file_id}
              onTranscriptionComplete={handleTranscriptionComplete}
            />
          </section>
        )}
        
        {/* Step 3: Generate Posts (Phase 3) */}
        {currentStep === 'generate' && transcription && (
          <section className="generation-section">
            <h2>📱 Step 3: Generate Social Media Posts</h2>
            <ErrorBoundary>
              <PostGenerator 
                transcriptionId={transcription.transcription_id}
                transcriptionText={transcription.text}
                onPostsGenerated={handlePostsGenerated}
              />
            </ErrorBoundary>
            
            <Posts posts={generatedPosts} />
          </section>
        )}
        
        {/* Reset button */}
        {currentStep !== 'upload' && (
          <div className="app-actions">
            <button onClick={resetApp} className="reset-button">
              🔄 Start Over
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
