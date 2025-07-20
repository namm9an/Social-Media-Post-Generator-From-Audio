import React, { useState, useEffect } from 'react';
import { 
  FiTwitter, 
  FiInstagram, 
  FiLinkedin, 
  FiFacebook,
  FiRefreshCw,
  FiSettings,
  FiCheckCircle,
  FiAlertCircle,
  FiCopy,
  FiEdit3,
  FiDownload,
  FiEye,
  FiEyeOff
} from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import NotificationService from '../../services/NotificationService';
import { CopyToClipboard } from 'react-copy-to-clipboard';

const PostGeneratorEnhanced = ({ 
  transcriptionId, 
  onPostsGenerated, 
  onErrorRecovery 
}) => {
  const [selectedPlatforms, setSelectedPlatforms] = useState(['twitter']);
  const [selectedTone, setSelectedTone] = useState('professional');
  const [generatedPosts, setGeneratedPosts] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [currentlyGenerating, setCurrentlyGenerating] = useState('');
  const [error, setError] = useState(null);
  const [showPreview, setShowPreview] = useState(true);
  const [editingPost, setEditingPost] = useState(null);
  const [editedContent, setEditedContent] = useState('');

  const platforms = [
    { 
      id: 'twitter', 
      name: 'Twitter', 
      icon: FiTwitter, 
      color: 'text-blue-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      maxChars: 280,
      features: ['hashtags', 'mentions', 'threads']
    },
    { 
      id: 'instagram', 
      name: 'Instagram', 
      icon: FiInstagram, 
      color: 'text-pink-500',
      bgColor: 'bg-pink-50',
      borderColor: 'border-pink-200',
      maxChars: 2200,
      features: ['hashtags', 'mentions', 'stories']
    },
    { 
      id: 'linkedin', 
      name: 'LinkedIn', 
      icon: FiLinkedin, 
      color: 'text-blue-700',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      maxChars: 3000,
      features: ['professional', 'articles', 'polls']
    },
    { 
      id: 'facebook', 
      name: 'Facebook', 
      icon: FiFacebook, 
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      maxChars: 63206,
      features: ['posts', 'events', 'groups']
    },
  ];

  const tones = [
    { id: 'professional', name: 'Professional', description: 'Formal and business-like' },
    { id: 'casual', name: 'Casual', description: 'Friendly and conversational' },
    { id: 'humorous', name: 'Humorous', description: 'Light and entertaining' },
    { id: 'inspiring', name: 'Inspiring', description: 'Motivational and uplifting' },
    { id: 'educational', name: 'Educational', description: 'Informative and instructional' },
    { id: 'promotional', name: 'Promotional', description: 'Marketing and sales-focused' },
  ];

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId) 
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const handleToneChange = (toneId) => {
    setSelectedTone(toneId);
  };

  const generatePosts = async () => {
    if (selectedPlatforms.length === 0) {
      NotificationService.validationError('Platform selection', 'Please select at least one platform');
      return;
    }

    setIsGenerating(true);
    setError(null);
    setGenerationProgress(0);
    setGeneratedPosts({});

    const toastId = NotificationService.generationProgress('', 0, selectedPlatforms.length);

    try {
      const response = await fetch('http://216.48.181.216:5000/api/generate-posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcription_id: transcriptionId,
          platforms: selectedPlatforms,
          tone: selectedTone,
        }),
      });

      if (!response.ok) {
        throw new Error('Post generation failed');
      }

      const result = await response.json();
      
      setGeneratedPosts(result.posts || {});
      setGenerationProgress(100);
      
      NotificationService.update(toastId, {
        render: 'Posts generated successfully!',
        type: 'success',
        isLoading: false,
        autoClose: 3000,
      });
      
      onPostsGenerated(result.posts || {});
      
    } catch (error) {
      setError(error.message);
      NotificationService.update(toastId, {
        render: 'Post generation failed. Please try again.',
        type: 'error',
        isLoading: false,
        autoClose: 5000,
      });
    } finally {
      setIsGenerating(false);
      setCurrentlyGenerating('');
    }
  };

  const regeneratePost = async (platform) => {
    setIsGenerating(true);
    setCurrentlyGenerating(platform);
    
    const toastId = NotificationService.generationProgress(platform, 0, 1);

    try {
      const response = await fetch('http://216.48.181.216:5000/api/regenerate-post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcription_id: transcriptionId,
          platform: platform,
          tone: selectedTone,
        }),
      });

      if (!response.ok) {
        throw new Error('Post regeneration failed');
      }

      const result = await response.json();
      
      setGeneratedPosts(prev => ({
        ...prev,
        [platform]: result.post
      }));
      
      NotificationService.update(toastId, {
        render: `${platform} post regenerated successfully!`,
        type: 'success',
        isLoading: false,
        autoClose: 3000,
      });
      
    } catch (error) {
      NotificationService.update(toastId, {
        render: 'Post regeneration failed. Please try again.',
        type: 'error',
        isLoading: false,
        autoClose: 5000,
      });
    } finally {
      setIsGenerating(false);
      setCurrentlyGenerating('');
    }
  };

  const handleEditPost = (platform, content) => {
    setEditingPost(platform);
    setEditedContent(content);
  };

  const handleSaveEdit = (platform) => {
    setGeneratedPosts(prev => ({
      ...prev,
      [platform]: editedContent
    }));
    setEditingPost(null);
    setEditedContent('');
    NotificationService.success('Post updated successfully');
  };

  const handleCancelEdit = () => {
    setEditingPost(null);
    setEditedContent('');
  };

  const handleCopy = (platform) => {
    NotificationService.copySuccess(`${platform} post`);
  };

  const getCharacterCount = (text) => {
    return text ? text.length : 0;
  };

  const getCharacterCountColor = (count, maxChars) => {
    const percentage = (count / maxChars) * 100;
    if (percentage >= 100) return 'text-red-600';
    if (percentage >= 80) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getPlatformIcon = (platformId) => {
    const platform = platforms.find(p => p.id === platformId);
    return platform ? platform.icon : FiSettings;
  };

  const getPlatformInfo = (platformId) => {
    return platforms.find(p => p.id === platformId) || platforms[0];
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      {/* Platform Selection */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Select Platforms</h3>
          <p className="text-sm text-gray-600">Choose the social media platforms you want to generate posts for</p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {platforms.map((platform) => {
              const Icon = platform.icon;
              const isSelected = selectedPlatforms.includes(platform.id);
              
              return (
                <motion.div
                  key={platform.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                    isSelected 
                      ? `${platform.borderColor} ${platform.bgColor} shadow-md` 
                      : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                  }`}
                  onClick={() => handlePlatformToggle(platform.id)}
                >
                  <div className="flex flex-col items-center space-y-2">
                    <Icon className={`w-8 h-8 ${isSelected ? platform.color : 'text-gray-400'}`} />
                    <span className={`text-sm font-medium ${isSelected ? 'text-gray-900' : 'text-gray-600'}`}>
                      {platform.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {platform.maxChars} chars
                    </span>
                  </div>
                  {isSelected && (
                    <div className="absolute top-2 right-2">
                      <FiCheckCircle className="w-5 h-5 text-green-500" />
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Tone Selection */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-gray-900">Select Tone</h3>
          <p className="text-sm text-gray-600">Choose the tone and style for your posts</p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {tones.map((tone) => {
              const isSelected = selectedTone === tone.id;
              
              return (
                <motion.div
                  key={tone.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 ${
                    isSelected 
                      ? 'border-primary-500 bg-primary-50 shadow-md' 
                      : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm'
                  }`}
                  onClick={() => handleToneChange(tone.id)}
                >
                  <div className="text-center">
                    <h4 className={`text-sm font-medium ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                      {tone.name}
                    </h4>
                    <p className={`text-xs ${isSelected ? 'text-primary-700' : 'text-gray-600'}`}>
                      {tone.description}
                    </p>
                  </div>
                  {isSelected && (
                    <div className="flex justify-center mt-2">
                      <FiCheckCircle className="w-4 h-4 text-primary-600" />
                    </div>
                  )}
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex justify-center">
        <button
          onClick={generatePosts}
          disabled={isGenerating || selectedPlatforms.length === 0}
          className="btn btn-primary btn-lg flex items-center space-x-3"
        >
          {isGenerating ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Generating Posts...</span>
            </>
          ) : (
            <>
              <FiSettings className="w-5 h-5" />
              <span>Generate Posts</span>
            </>
          )}
        </button>
      </div>

      {/* Generation Progress */}
      {isGenerating && (
        <div className="card">
          <div className="card-body">
            <div className="text-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Generating Posts</h3>
              <p className="text-sm text-gray-600">
                {currentlyGenerating ? `Creating ${currentlyGenerating} post...` : 'Processing your request...'}
              </p>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${generationProgress}%` }}
              />
            </div>
            <div className="text-center mt-2">
              <span className="text-sm text-gray-600">{generationProgress}% complete</span>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="card border-red-200 bg-red-50">
          <div className="card-body">
            <div className="flex items-center space-x-3">
              <FiAlertCircle className="w-6 h-6 text-red-500" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Generation Failed</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
            <div className="mt-4 flex space-x-3">
              <button
                onClick={generatePosts}
                className="btn btn-sm btn-error flex items-center space-x-1"
              >
                <FiRefreshCw className="w-4 h-4" />
                <span>Retry</span>
              </button>
              <button
                onClick={onErrorRecovery}
                className="btn btn-sm btn-secondary"
              >
                Go Back
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generated Posts */}
      {Object.keys(generatedPosts).length > 0 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900">Generated Posts</h3>
            <button
              onClick={() => setShowPreview(!showPreview)}
              className="btn btn-sm btn-ghost flex items-center space-x-1"
            >
              {showPreview ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
              <span>{showPreview ? 'Hide' : 'Show'} Preview</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(generatedPosts).map(([platform, content]) => {
              const platformInfo = getPlatformInfo(platform);
              const Icon = platformInfo.icon;
              const charCount = getCharacterCount(content);
              const isEditing = editingPost === platform;
              
              return (
                <motion.div
                  key={platform}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card"
                >
                  <div className="card-header">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Icon className={`w-6 h-6 ${platformInfo.color}`} />
                        <div>
                          <h4 className="text-lg font-semibold text-gray-900">{platformInfo.name}</h4>
                          <p className={`text-sm ${getCharacterCountColor(charCount, platformInfo.maxChars)}`}>
                            {charCount}/{platformInfo.maxChars} characters
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => regeneratePost(platform)}
                          disabled={isGenerating}
                          className="btn btn-sm btn-ghost flex items-center space-x-1"
                        >
                          <FiRefreshCw className={`w-4 h-4 ${currentlyGenerating === platform ? 'animate-spin' : ''}`} />
                          <span>Regenerate</span>
                        </button>
                        <CopyToClipboard text={content} onCopy={() => handleCopy(platform)}>
                          <button className="btn btn-sm btn-ghost flex items-center space-x-1">
                            <FiCopy className="w-4 h-4" />
                            <span>Copy</span>
                          </button>
                        </CopyToClipboard>
                      </div>
                    </div>
                  </div>

                  <div className="card-body">
                    {isEditing ? (
                      <div className="space-y-4">
                        <textarea
                          value={editedContent}
                          onChange={(e) => setEditedContent(e.target.value)}
                          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                          placeholder={`Edit your ${platform} post here...`}
                        />
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={handleCancelEdit}
                            className="btn btn-sm btn-secondary"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handleSaveEdit(platform)}
                            className="btn btn-sm btn-primary"
                          >
                            Save
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div 
                          className={`p-4 rounded-lg border-2 ${platformInfo.borderColor} ${platformInfo.bgColor}`}
                        >
                          <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                            {content}
                          </p>
                        </div>
                        <div className="flex justify-end">
                          <button
                            onClick={() => handleEditPost(platform, content)}
                            className="btn btn-sm btn-ghost flex items-center space-x-1"
                          >
                            <FiEdit3 className="w-4 h-4" />
                            <span>Edit</span>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default PostGeneratorEnhanced;
