import React from 'react';

interface Props {
  data: {
    id?: string;
    root_cause_category: string;
    root_cause_text: string;
    recommended_corrective_action: string;
    recommended_preventive_action: string;
    ai_confidence: string;
  };
}

const CAPAResults: React.FC<Props> = ({ data }) => {
  if (!data) {
    return (
      <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 text-sm">
        No CAPA recommendations available.
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-3">
      <p className="text-sm font-medium text-slate-700">CAPA Recommendation</p>

      {/* Root Cause Summary */}
      <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
        <p className="text-xs font-bold text-slate-500 uppercase mb-1">Root Cause ({data.root_cause_category})</p>
        <p className="text-sm text-slate-700">{data.root_cause_text}</p>
      </div>

      {/* Corrective Action */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-blue-500" />
          <p className="text-xs font-bold text-blue-700 uppercase">Corrective Action</p>
          <span className="text-[10px] text-blue-500 ml-auto">(Fixes this instance)</span>
        </div>
        <p className="text-sm text-blue-900 leading-relaxed">{data.recommended_corrective_action}</p>
      </div>

      {/* Preventive Action */}
      <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <p className="text-xs font-bold text-green-700 uppercase">Preventive Action</p>
          <span className="text-[10px] text-green-500 ml-auto">(Stops recurrence)</span>
        </div>
        <p className="text-sm text-green-900 leading-relaxed">{data.recommended_preventive_action}</p>
      </div>

      <p className="text-xs text-slate-400 italic">
        AI-suggested CAPA for human review. Corrective actions fix the immediate issue; preventive actions address systemic causes.
      </p>
    </div>
  );
};

export default CAPAResults;
