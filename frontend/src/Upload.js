import React from 'react';

function Upload({ onTranscriptionComplete, onPostsGenerated, isProcessing, setIsProcessing }) {
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setIsProcessing(true);
      const formData = new FormData();
      formData.append('file', file);

      try {
        // Simulate file upload and transcription
        setTimeout(() => {
          const mockTranscription = "This is a mock transcription of the audio file.";
          onTranscriptionComplete(mockTranscription);
          
          const mockPosts = {
            linkedin: "LinkedIn Post:
 This is a mock LinkedIn post.",
            twitter: "Twitter Post: This is a mock tweet.",
            instagram: "Instagram Post:
 This is a mock Instagram caption."
          };
          onPostsGenerated(mockPosts);
          setIsProcessing(false);
        }, 2000);

      } catch (error) {
        console.error("Error uploading file", error);
        setIsProcessing(false);
      }
    }
  };

  return (
    <div className="upload-section">
      <input 
        type="file" 
        accept=".mp3,.wav,.m4a" 
        onChange={handleFileChange}
        disabled={isProcessing}
      />
      {isProcessing && <p>Processing... Please wait.</p>}
    </div>
  );
}

export default Upload;
