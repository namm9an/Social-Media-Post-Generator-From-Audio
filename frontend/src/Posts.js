import React from 'react';

function Posts({ posts }) {
  if (!posts || Object.keys(posts).length === 0) {
    return null;
  }

  return (
    <div className="posts-section">
      <h2>📱 Generated Social Media Posts</h2>
      
      {posts.linkedin && (
        <div className="post-card linkedin">
          <h3>💼 LinkedIn</h3>
          <p>{posts.linkedin}</p>
        </div>
      )}
      
      {posts.twitter && (
        <div className="post-card twitter">
          <h3>🐦 Twitter</h3>
          <p>{posts.twitter}</p>
        </div>
      )}
      
      {posts.instagram && (
        <div className="post-card instagram">
          <h3>📸 Instagram</h3>
          <p>{posts.instagram}</p>
        </div>
      )}
    </div>
  );
}

export default Posts;
