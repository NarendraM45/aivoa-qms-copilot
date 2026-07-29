import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';

const ExtractionProgressBar: React.FC = () => {
  const { uploadState, extractionProgress, currentNode } = useSelector((state: RootState) => state.aiPanel);

  if (uploadState !== 'extracting' && uploadState !== 'uploading') return null;

  const nodeMessages: Record<string, string> = {
    'parse_document': 'Parsing document structure...',
    'extract_fields': 'Extracting complaint fields using AI...',
    'check_completeness': 'Evaluating data completeness...',
    'classify_severity': 'Classifying risk & severity...',
    'detect_duplicates': 'Scanning for potential duplicates...',
    'generate_summary': 'Generating complaint summary...',
  };

  const statusText = nodeMessages[currentNode] || currentNode || (uploadState === 'uploading' ? 'Uploading document...' : 'Processing...');

  return (
    <div className="mb-4 bg-white border border-slate-200 p-4 rounded-lg shadow-sm">
      <div className="flex justify-between items-end mb-2">
        <span className="text-sm font-medium text-slate-700">{statusText}</span>
        <span className="text-xs font-bold text-blue-600">{Math.round(extractionProgress)}%</span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
        <div 
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out bg-[length:1rem_1rem] bg-[linear-gradient(45deg,rgba(255,255,255,0.15)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.15)_50%,rgba(255,255,255,0.15)_75%,transparent_75%,transparent)] animate-[progress_1s_linear_infinite]" 
          style={{ width: `${extractionProgress}%` }}
        ></div>
      </div>
      <style>{`
        @keyframes progress {
          from { background-position: 1rem 0; }
          to { background-position: 0 0; }
        }
      `}</style>
    </div>
  );
};

export default ExtractionProgressBar;
