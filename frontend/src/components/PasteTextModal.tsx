import React, { useState } from 'react';
import { useExtraction } from '../hooks/useExtraction';
import { X } from 'lucide-react';

interface Props {
  onClose: () => void;
}

const PasteTextModal: React.FC<Props> = ({ onClose }) => {
  const [text, setText] = useState('');
  const { pasteText, isLoading } = useExtraction();

  const handleExtract = () => {
    if (text.trim()) {
      pasteText(text);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
          <h3 className="font-bold text-slate-800">Paste Complaint Text</h3>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-700 transition-colors">
            <X size={20} />
          </button>
        </div>
        <div className="p-6">
          <textarea 
            value={text} 
            onChange={(e) => setText(e.target.value)} 
            placeholder="Paste raw email, letter, or notes here..."
            className="w-full h-64 p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none resize-none"
          ></textarea>
        </div>
        <div className="px-6 py-4 border-t border-slate-200 bg-slate-50 flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 border border-slate-300 rounded-md text-slate-700 font-medium hover:bg-slate-100 transition-colors">
            Cancel
          </button>
          <button 
            onClick={handleExtract} 
            disabled={!text.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            Extract Information
          </button>
        </div>
      </div>
    </div>
  );
};

export default PasteTextModal;
