import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface Props {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

const FormSection: React.FC<Props> = ({ title, children, defaultOpen = true }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-l-4 border-blue-500 bg-white rounded-r-md shadow-sm mb-4 border border-slate-200 overflow-hidden">
      <button 
        className="w-full px-4 py-3 bg-slate-50 flex items-center justify-between hover:bg-slate-100 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
        type="button"
      >
        <h3 className="font-semibold text-slate-800">{title}</h3>
        {isOpen ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
      </button>
      {isOpen && (
        <div className="p-4 bg-white grid grid-cols-1 md:grid-cols-2 gap-4">
          {children}
        </div>
      )}
    </div>
  );
};

export default FormSection;
