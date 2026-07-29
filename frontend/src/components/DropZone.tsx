import React, { useState } from 'react';
import { UploadCloud, FileText } from 'lucide-react';
import { useExtraction } from '../hooks/useExtraction';
import PasteTextModal from './PasteTextModal';

const DropZone: React.FC = () => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [showPasteModal, setShowPasteModal] = useState(false);
  const { uploadFile } = useExtraction();

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const onDragLeave = () => setIsDragActive(false);

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  return (
    <div className="mb-4">
      <div 
        onDragOver={onDragOver} 
        onDragLeave={onDragLeave} 
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-lg p-6 flex flex-col items-center justify-center transition-colors ${
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-slate-50 hover:bg-slate-100'
        }`}
      >
        <UploadCloud className="w-10 h-10 text-slate-400 mb-3" />
        <p className="text-sm font-medium text-slate-700 text-center mb-1">Drop complaint document here</p>
        <p className="text-xs text-slate-500 mb-4">PDF, DOCX, TXT, EML up to 10MB</p>
        
        <div className="flex gap-3">
          <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
            Browse Files
            <input type="file" className="hidden" accept=".pdf,.docx,.txt,.eml" onChange={onFileChange} />
          </label>
          <button 
            onClick={() => setShowPasteModal(true)}
            className="bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2"
          >
            <FileText size={16} /> Paste Text
          </button>
        </div>
      </div>
      {showPasteModal && <PasteTextModal onClose={() => setShowPasteModal(false)} />}
    </div>
  );
};

export default DropZone;
