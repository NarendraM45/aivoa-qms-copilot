import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../store';
import { setField } from '../store/complaintFormSlice';

interface Props {
  fieldName: keyof Omit<RootState['complaintForm'], 'complaintId' | 'status' | 'isSaving' | 'saveError'>;
  label: string;
  type: 'text' | 'select' | 'date' | 'textarea' | 'number';
  options?: { value: string; label: string }[];
  placeholder?: string;
}

const AIFormField: React.FC<Props> = ({ fieldName, label, type, options, placeholder = 'Awaiting AI extraction...' }) => {
  const dispatch = useDispatch();
  const fieldData = useSelector((state: RootState) => state.complaintForm[fieldName] as any);
  const [highlight, setHighlight] = useState(false);

  useEffect(() => {
    if (fieldData?.source === 'ai' && fieldData?.value) {
      setHighlight(true);
      const timer = setTimeout(() => setHighlight(false), 800);
      return () => clearTimeout(timer);
    }
  }, [fieldData?.value, fieldData?.source]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    dispatch(setField({ field: fieldName, value: e.target.value, source: 'user', confidence: fieldData?.confidence }));
  };

  const getConfidenceColor = (score: number | null) => {
    if (score === null) return '';
    if (score >= 0.8) return 'text-green-500';
    if (score >= 0.5) return 'text-amber-500';
    return 'text-red-500';
  };

  const isLowConfidence = fieldData?.confidence !== null && fieldData?.confidence < 0.5;

  const baseInputClass = `w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors ${
    highlight ? 'bg-blue-50 border-blue-300' : 
    isLowConfidence ? 'bg-red-50 border-red-300' : 'bg-white border-slate-300'
  }`;

  return (
    <div className="flex flex-col space-y-1 mb-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-700">{label}</label>
        {fieldData?.source === 'ai' && (
          <div className="flex items-center space-x-2">
            <span className="text-[10px] uppercase font-bold bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">AI</span>
            {fieldData.confidence !== null && (
              <span className={`text-xs flex items-center ${getConfidenceColor(fieldData.confidence)}`} title={`Confidence: ${(fieldData.confidence * 100).toFixed(0)}%`}>
                ●
              </span>
            )}
          </div>
        )}
      </div>
      
      {type === 'select' && options ? (
        <select value={fieldData?.value || ''} onChange={handleChange} className={baseInputClass}>
          <option value="" disabled>{placeholder}</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      ) : type === 'textarea' ? (
        <textarea value={fieldData?.value || ''} onChange={handleChange} placeholder={placeholder} className={`${baseInputClass} min-h-[100px] resize-y`} />
      ) : (
        <input type={type} value={fieldData?.value || ''} onChange={handleChange} placeholder={placeholder} className={baseInputClass} />
      )}
    </div>
  );
};

export default AIFormField;
