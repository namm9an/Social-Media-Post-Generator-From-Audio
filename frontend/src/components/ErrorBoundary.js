import React from 'react';
import { FiAlertTriangle, FiRefreshCw, FiHome, FiMail, FiChevronDown, FiChevronUp } from 'react-icons/fi';
import { motion } from 'framer-motion';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      showDetails: false,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    return { 
      hasError: true,
      errorId: Date.now().toString(36) + Math.random().toString(36).substr(2)
    };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Log error to console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // You can also log the error to an error reporting service here
    // logErrorToService(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
      errorId: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  toggleDetails = () => {
    this.setState(prevState => ({
      showDetails: !prevState.showDetails
    }));
  };

  reportError = () => {
    const errorReport = {
      errorId: this.state.errorId,
      error: this.state.error?.toString(),
      errorInfo: this.state.errorInfo?.componentStack,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      url: window.location.href
    };

    const mailtoLink = `mailto:support@example.com?subject=Error Report - ID: ${this.state.errorId}&body=${encodeURIComponent(
      JSON.stringify(errorReport, null, 2)
    )}`;
    
    window.location.href = mailtoLink;
  };

  getErrorMessage = () => {
    if (!this.state.error) return 'An unexpected error occurred';
    
    const errorMessage = this.state.error.toString();
    
    // Provide user-friendly error messages based on common error types
    if (errorMessage.includes('Network Error') || errorMessage.includes('fetch')) {
      return 'Unable to connect to the server. Please check your internet connection.';
    }
    
    if (errorMessage.includes('ChunkLoadError')) {
      return 'Failed to load application resources. Please refresh the page.';
    }
    
    if (errorMessage.includes('SyntaxError')) {
      return 'There was a problem loading the application. Please try refreshing the page.';
    }
    
    return 'An unexpected error occurred. Please try again.';
  };

  getRecoveryActions = () => {
    const errorMessage = this.state.error?.toString() || '';
    
    if (errorMessage.includes('Network Error') || errorMessage.includes('fetch')) {
      return [
        'Check your internet connection',
        'Wait a moment and try again',
        'Contact support if the problem persists'
      ];
    }
    
    if (errorMessage.includes('ChunkLoadError')) {
      return [
        'Refresh the page to reload resources',
        'Clear your browser cache',
        'Try using a different browser'
      ];
    }
    
    return [
      'Try refreshing the page',
      'Check if the issue persists',
      'Contact support if needed'
    ];
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl w-full"
          >
            <div className="card border-red-200 bg-red-50">
              <div className="card-body text-center py-12">
                <div className="flex justify-center mb-6">
                  <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center">
                    <FiAlertTriangle className="w-10 h-10 text-red-600" />
                  </div>
                </div>
                
                <h1 className="text-2xl font-bold text-gray-900 mb-4">
                  Oops! Something went wrong
                </h1>
                
                <p className="text-gray-700 mb-8 text-lg">
                  {this.getErrorMessage()}
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                  <button
                    onClick={this.handleRetry}
                    className="btn btn-primary flex items-center justify-center space-x-2"
                  >
                    <FiRefreshCw className="w-5 h-5" />
                    <span>Try Again</span>
                  </button>
                  
                  <button
                    onClick={this.handleReload}
                    className="btn btn-secondary flex items-center justify-center space-x-2"
                  >
                    <FiRefreshCw className="w-5 h-5" />
                    <span>Reload Page</span>
                  </button>
                  
                  <button
                    onClick={this.handleGoHome}
                    className="btn btn-secondary flex items-center justify-center space-x-2"
                  >
                    <FiHome className="w-5 h-5" />
                    <span>Go Home</span>
                  </button>
                </div>
                
                {/* Recovery Actions */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-blue-900 mb-4">What you can try:</h3>
                  <ul className="text-left space-y-2 text-blue-800">
                    {this.getRecoveryActions().map((action, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <span className="text-blue-600 font-bold">•</span>
                        <span>{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                {/* Error Details */}
                <div className="text-left">
                  <button
                    onClick={this.toggleDetails}
                    className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors mb-4"
                  >
                    {this.state.showDetails ? (
                      <FiChevronUp className="w-4 h-4" />
                    ) : (
                      <FiChevronDown className="w-4 h-4" />
                    )}
                    <span>Technical Details</span>
                  </button>
                  
                  {this.state.showDetails && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="bg-gray-100 rounded-lg p-4 mb-4 text-sm font-mono text-gray-800"
                    >
                      <div className="mb-4">
                        <strong>Error ID:</strong> {this.state.errorId}
                      </div>
                      <div className="mb-4">
                        <strong>Error:</strong>
                        <pre className="mt-1 whitespace-pre-wrap">
                          {this.state.error && this.state.error.toString()}
                        </pre>
                      </div>
                      <div>
                        <strong>Component Stack:</strong>
                        <pre className="mt-1 whitespace-pre-wrap text-xs">
                          {this.state.errorInfo?.componentStack}
                        </pre>
                      </div>
                    </motion.div>
                  )}
                </div>
                
                {/* Report Error */}
                <div className="flex justify-center">
                  <button
                    onClick={this.reportError}
                    className="btn btn-ghost flex items-center space-x-2 text-gray-600 hover:text-gray-800"
                  >
                    <FiMail className="w-4 h-4" />
                    <span>Report this error</span>
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      );
    }
    
    return this.props.children;
  }
}

export default ErrorBoundary;
