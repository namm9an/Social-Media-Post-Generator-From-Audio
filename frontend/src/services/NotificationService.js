import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

class NotificationService {
  static initialized = false;

  static init() {
    if (!this.initialized) {
      this.initialized = true;
      // Configure toast default options
      toast.configure({
        position: 'top-right',
        autoClose: 5000,
        hideProgressBar: false,
        newestOnTop: true,
        closeOnClick: true,
        rtl: false,
        pauseOnFocusLoss: false,
        draggable: true,
        pauseOnHover: true,
        className: 'toast-notification',
        bodyClassName: 'toast-body',
        progressClassName: 'toast-progress',
      });
    }
  }

  static success(message, options = {}) {
    this.init();
    toast.success(message, {
      className: 'toast-success',
      icon: '✅',
      ...options,
    });
  }

  static error(message, options = {}) {
    this.init();
    toast.error(message, {
      className: 'toast-error',
      icon: '❌',
      autoClose: 8000, // Longer duration for errors
      ...options,
    });
  }

  static warning(message, options = {}) {
    this.init();
    toast.warning(message, {
      className: 'toast-warning',
      icon: '⚠️',
      ...options,
    });
  }

  static info(message, options = {}) {
    this.init();
    toast.info(message, {
      className: 'toast-info',
      icon: 'ℹ️',
      ...options,
    });
  }

  static loading(message, options = {}) {
    this.init();
    return toast.loading(message, {
      className: 'toast-loading',
      icon: '⏳',
      ...options,
    });
  }

  static update(toastId, options = {}) {
    this.init();
    toast.update(toastId, options);
  }

  static dismiss(toastId) {
    this.init();
    toast.dismiss(toastId);
  }

  static dismissAll() {
    this.init();
    toast.dismiss();
  }

  // Custom notifications with more detailed information
  static uploadProgress(fileName, progress) {
    this.init();
    return toast.info(
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">Uploading {fileName}</p>
          <div className="mt-1 bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">{progress}% complete</p>
        </div>
      </div>,
      {
        autoClose: false,
        hideProgressBar: true,
        closeOnClick: false,
        draggable: false,
        className: 'toast-upload-progress',
      }
    );
  }

  static transcriptionProgress(status, confidence) {
    this.init();
    return toast.info(
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">Transcribing Audio</p>
          <p className="text-xs text-gray-500">{status}</p>
          {confidence && (
            <p className="text-xs text-gray-500">Confidence: {Math.round(confidence * 100)}%</p>
          )}
        </div>
      </div>,
      {
        autoClose: false,
        hideProgressBar: true,
        closeOnClick: false,
        draggable: false,
        className: 'toast-transcription-progress',
      }
    );
  }

  static generationProgress(platform, completed, total) {
    this.init();
    return toast.info(
      <div className="flex items-center space-x-3">
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-purple-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900">Generating Posts</p>
          <p className="text-xs text-gray-500">
            {platform ? `Creating ${platform} content` : 'Processing...'}
          </p>
          {completed && total && (
            <p className="text-xs text-gray-500">{completed} of {total} platforms completed</p>
          )}
        </div>
      </div>,
      {
        autoClose: false,
        hideProgressBar: true,
        closeOnClick: false,
        draggable: false,
        className: 'toast-generation-progress',
      }
    );
  }

  static copySuccess(itemName) {
    this.init();
    toast.success(`${itemName} copied to clipboard!`, {
      icon: '📋',
      autoClose: 2000,
      className: 'toast-copy-success',
    });
  }

  static downloadSuccess(fileName) {
    this.init();
    toast.success(`${fileName} downloaded successfully!`, {
      icon: '📥',
      autoClose: 3000,
      className: 'toast-download-success',
    });
  }

  static validationError(fieldName, message) {
    this.init();
    toast.error(
      <div>
        <p className="font-medium">{fieldName} validation failed</p>
        <p className="text-sm text-red-100">{message}</p>
      </div>,
      {
        icon: '⚠️',
        autoClose: 6000,
        className: 'toast-validation-error',
      }
    );
  }

  static networkError(message = 'Network connection failed') {
    this.init();
    toast.error(
      <div>
        <p className="font-medium">Connection Error</p>
        <p className="text-sm text-red-100">{message}</p>
        <p className="text-xs text-red-200 mt-1">Please check your internet connection</p>
      </div>,
      {
        icon: '🌐',
        autoClose: 8000,
        className: 'toast-network-error',
      }
    );
  }

  static processingError(operation, error) {
    this.init();
    toast.error(
      <div>
        <p className="font-medium">{operation} failed</p>
        <p className="text-sm text-red-100">{error}</p>
        <p className="text-xs text-red-200 mt-1">Please try again or contact support</p>
      </div>,
      {
        icon: '❌',
        autoClose: 10000,
        className: 'toast-processing-error',
      }
    );
  }

  static customNotification(type, title, message, options = {}) {
    this.init();
    const notificationContent = (
      <div>
        <p className="font-medium">{title}</p>
        <p className="text-sm opacity-90">{message}</p>
      </div>
    );

    switch (type) {
      case 'success':
        return toast.success(notificationContent, options);
      case 'error':
        return toast.error(notificationContent, options);
      case 'warning':
        return toast.warning(notificationContent, options);
      case 'info':
      default:
        return toast.info(notificationContent, options);
    }
  }
}

export default NotificationService;
