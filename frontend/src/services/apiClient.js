import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Configure axios defaults
axios.defaults.baseURL = API_BASE;
axios.defaults.timeout = 30000; // 30 seconds timeout

class ApiClient {
  constructor() {
    this.baseURL = API_BASE;
  }

  /**
   * Upload audio file to backend
   * @param {File} file - Audio file to upload
   * @returns {Promise<Object>} Upload result
   */
  async uploadAudio(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          console.log(`Upload progress: ${percentCompleted}%`);
        },
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Upload error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
        errors: error.response?.data?.errors || [],
      };
    }
  }

  /**
   * Start transcription process
   * @param {string} fileId - ID of uploaded file
   * @returns {Promise<Object>} Transcription result
   */
  async startTranscription(fileId) {
    try {
      const response = await axios.post('/api/transcribe', {
        file_id: fileId,
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Transcription error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  /**
   * Get transcription status and result
   * @param {string} transcriptionId - ID of transcription
   * @returns {Promise<Object>} Transcription status/result
   */
  async getTranscriptionStatus(transcriptionId) {
    try {
      const response = await axios.get(`/api/transcription/${transcriptionId}`);

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get transcription error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  /**
   * Delete uploaded file
   * @param {string} fileId - ID of file to delete
   * @returns {Promise<Object>} Deletion result
   */
  async deleteFile(fileId) {
    try {
      const response = await axios.delete(`/api/files/${fileId}`);

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Delete file error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async checkHealth() {
    try {
      const response = await axios.get('/api/health');

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Health check error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  /**
   * Generate social media posts from transcription
   * @param {string} transcriptionId - ID of transcription
   * @param {Array} platforms - Array of platform names
   * @param {string} tone - Tone for post generation
   * @returns {Promise<Object>} Generated posts
   */
  async generatePosts(transcriptionId, platforms, tone) {
    try {
      const response = await axios.post('/api/generate-posts', {
        transcription_id: transcriptionId,
        platforms,
        tone,
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Generate posts error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  /**
   * Regenerate specific post with different tone
   * @param {string} transcriptionId - ID of transcription
   * @param {string} platform - Platform name
   * @param {string} tone - New tone for regeneration
   * @returns {Promise<Object>} Regenerated post
   */
  async regeneratePost(transcriptionId, platform, tone) {
    try {
      const response = await axios.post('/api/regenerate-post', {
        transcription_id: transcriptionId,
        platform,
        tone,
      });

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Regenerate post error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  /**
   * Get generated posts by post ID
   * @param {string} postId - ID of post
   * @returns {Promise<Object>} Post data
   */
  async getPosts(postId) {
    try {
      const response = await axios.get(`/api/posts/${postId}`);

      return {
        success: true,
        data: response.data,
      };
    } catch (error) {
      console.error('Get posts error:', error);
      return {
        success: false,
        error: error.response?.data?.error || error.message,
      };
    }
  }

  /**
   * Validate file before upload
   * @param {File} file - File to validate
   * @returns {Object} Validation result
   */
  validateFile(file) {
    const maxSize = (process.env.REACT_APP_MAX_FILE_SIZE || 50) * 1024 * 1024; // Convert MB to bytes
    const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg', 'audio/flac'];
    const allowedExtensions = ['mp3', 'wav', 'm4a', 'ogg', 'flac'];

    const errors = [];

    // Check file size
    if (file.size > maxSize) {
      errors.push(`File size (${(file.size / (1024 * 1024)).toFixed(1)}MB) exceeds maximum allowed size (${maxSize / (1024 * 1024)}MB)`);
    }

    // Check file extension
    const extension = file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(extension)) {
      errors.push(`Invalid file format. Supported formats: ${allowedExtensions.join(', ')}`);
    }

    // Check MIME type
    if (!allowedTypes.includes(file.type) && file.type !== '') {
      errors.push(`Invalid file type: ${file.type}`);
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  /**
   * Format file size for display
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Format duration for display
   * @param {number} seconds - Duration in seconds
   * @returns {string} Formatted duration
   */
  formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
}

// Export singleton instance
const apiClient = new ApiClient();
export default apiClient;

// Export standalone functions for convenience
export const generatePosts = async (transcriptionId, platforms, tone) => {
  const result = await apiClient.generatePosts(transcriptionId, platforms, tone);
  if (result.success) {
    return result.data;
  } else {
    throw new Error(result.error);
  }
};

export const regeneratePost = async (transcriptionId, platform, tone) => {
  const result = await apiClient.regeneratePost(transcriptionId, platform, tone);
  if (result.success) {
    return result.data;
  } else {
    throw new Error(result.error);
  }
};

export const getPosts = async (postId) => {
  const result = await apiClient.getPosts(postId);
  if (result.success) {
    return result.data;
  } else {
    throw new Error(result.error);
  }
};
