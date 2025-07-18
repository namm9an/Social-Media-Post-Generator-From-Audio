import React from 'react';
import { FiCopy, FiDownload, FiMail, FiShare2 } from 'react-icons/fi';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { saveAs } from 'file-saver';
import NotificationService from '../services/NotificationService';

const PostExport = ({ posts, onExportReady, onErrorRecovery }) => {
  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(posts, null, 2)], {
      type: 'application/json',
    });
    saveAs(blob, 'generated_posts.json');
    NotificationService.downloadSuccess('Posts JSON');
  };

  const downloadPDF = () => {
    // Placeholder function: Implement PDF generation logic
    NotificationService.info('PDF export is currently unavailable.');
  };

  const emailShare = () => {
    const mailtoLink = `mailto:?subject=Generated Social Media Posts&body=${encodeURIComponent(
      JSON.stringify(posts, null, 2)
    )}`;
    window.location.href = mailtoLink;
  };

  const handleCopyAll = () => {
    NotificationService.copySuccess('All posts');
  };

  const renderPost = (platform, content) => (
    <div key={platform} className="card mb-4">
      <div className="card-header">
        <h3 className="text-lg font-semibold text-gray-900">
          {platform.charAt(0).toUpperCase() + platform.slice(1)}
        </h3>
      </div>
      <div className="card-body">
        <p className="text-gray-800 whitespace-pre-wrap">{content}</p>
        <div className="flex justify-end mt-4">
          <CopyToClipboard text={content} onCopy={() => NotificationService.copySuccess(`${platform} post`)}>
            <button className="btn btn-sm btn-ghost flex items-center space-x-1">
              <FiCopy className="w-4 h-4" />
              <span>Copy</span>
            </button>
          </CopyToClipboard>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Export & Share Your Posts</h2>
        <div className="flex space-x-2">
          <button onClick={downloadJSON} className="btn btn-secondary btn-sm flex items-center space-x-1">
            <FiDownload className="w-4 h-4" />
            <span>Download JSON</span>
          </button>
          <button onClick={downloadPDF} className="btn btn-secondary btn-sm flex items-center space-x-1">
            <FiDownload className="w-4 h-4" />
            <span>Download PDF</span>
          </button>
          <button onClick={emailShare} className="btn btn-secondary btn-sm flex items-center space-x-1">
            <FiMail className="w-4 h-4" />
            <span>Share via Email</span>
          </button>
          <CopyToClipboard text={JSON.stringify(posts, null, 2)} onCopy={handleCopyAll}>
            <button className="btn btn-secondary btn-sm flex items-center space-x-1">
              <FiCopy className="w-4 h-4" />
              <span>Copy All</span>
            </button>
          </CopyToClipboard>
        </div>
      </div>
      <div>
        {Object.entries(posts).map(([platform, content]) => renderPost(platform, content))}
      </div>
      <div className="flex justify-center mt-8">
        <button
          onClick={() => onExportReady()}
          className="btn btn-primary btn-lg flex items-center space-x-2"
        >
          <FiShare2 className="w-5 h-5" />
          <span>Finish Export & Proceed</span>
        </button>
      </div>
    </div>
  );
};

export default PostExport;

