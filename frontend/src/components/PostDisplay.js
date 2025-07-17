import React from 'react';

const PostDisplay = ({ posts, onRegenerate, onCopy }) => {
  return (
    <div className="post-display">
      {Object.keys(posts).map((platform) => (
        <div key={platform} className={`post-card ${platform}`}>
          <h4>{platform.charAt(0).toUpperCase() + platform.slice(1)} Post</h4>
          <textarea value={posts[platform]} readOnly></textarea>
          <div className="post-actions">
            <button onClick={() => onCopy(platform)}>Copy to Clipboard</button>
            <button onClick={() => onRegenerate(platform)}>Regenerate</button>
          </div>
          <div className="character-count">
            {posts[platform].length} characters
          </div>
        </div>
      ))}
    </div>
  );
};

export default PostDisplay;
