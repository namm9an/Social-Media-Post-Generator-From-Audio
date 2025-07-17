import React, { useState } from 'react';
import ToneSelector from './ToneSelector';
import PlatformSelector from './PlatformSelector';
import PostDisplay from './PostDisplay';
import { generatePosts, regeneratePost } from '../services/apiClient';

const PostGenerator = ({ transcriptionId, transcriptionText, onPostsGenerated }) => {
  const [tone, setTone] = useState('professional');
  const [platforms, setPlatforms] = useState([]);
  const [posts, setPosts] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (platforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await generatePosts(transcriptionId, platforms, tone);
      setPosts(response.posts);
      if (onPostsGenerated) {
        onPostsGenerated(response.posts);
      }
    } catch (err) {
      setError('Failed to generate posts: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async (platform) => {
    setLoading(true);
    setError('');

    try {
      const response = await regeneratePost(transcriptionId, platform, tone);
      setPosts(prev => ({ ...prev, [platform]: response.post }));
    } catch (err) {
      setError('Failed to regenerate post: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (platform) => {
    const text = posts[platform];
    navigator.clipboard.writeText(text).then(() => {
      alert(`${platform} post copied to clipboard!`);
    });
  };

  return (
    <div className="post-generator">
      <h2>Generate Social Media Posts</h2>
      
      <div className="transcription-preview">
        <h3>Source Transcription</h3>
        <p>{transcriptionText}</p>
      </div>

      <ToneSelector selectedTone={tone} onToneChange={setTone} />
      <PlatformSelector selectedPlatforms={platforms} onPlatformChange={setPlatforms} />

      <button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Generating...' : 'Generate Posts'}
      </button>

      {error && <div className="error">{error}</div>}

      {Object.keys(posts).length > 0 && (
        <PostDisplay 
          posts={posts} 
          onRegenerate={handleRegenerate} 
          onCopy={handleCopy} 
        />
      )}
    </div>
  );
};

export default PostGenerator;
