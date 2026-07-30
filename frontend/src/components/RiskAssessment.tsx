import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';
import { ShieldAlert } from 'lucide-react';

const RiskAssessmentPanel: React.FC = () => {
  const risk = useSelector((state: RootState) => state.aiPanel.riskAssessment);
  
  const hasSomething = risk.severity || risk.priority || risk.nextAction || risk.justification;
  
  if (!hasSomething) {
    return (
      <div className="bg-white rounded-lg p-6 border border-slate-200">
        <div className="flex items-center gap-2 mb-4">
          <ShieldAlert size={20} className="text-slate-800" />
          <h3 className="text-base font-semibold text-slate-800">AI copilot risk assessment</h3>
        </div>
        <p className="text-sm text-slate-500 italic">No risk assessment data available yet.</p>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-lg p-6 border border-slate-200">
      <div className="flex items-center gap-2 mb-6">
        <ShieldAlert size={20} className="text-slate-800" />
        <h3 className="text-base font-semibold text-slate-800">AI copilot risk assessment</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Left: Severity */}
        <div>
          <div className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-xs font-semibold mb-2">
            Severity (Suggested)
          </div>
          <div className="border border-slate-200 rounded-md p-3 bg-slate-50 text-sm text-slate-700">
            {risk.severity ? risk.severity.charAt(0).toUpperCase() + risk.severity.slice(1) : 'Not assessed'}
          </div>
        </div>
        
        {/* Right: Suggested Next Action */}
        <div>
          <div className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-xs font-semibold mb-2">
            Suggested Next Action
          </div>
          <div className="border border-slate-200 rounded-md p-3 bg-slate-50 text-sm text-slate-700">
            {risk.nextAction || 'Not assessed'}
          </div>
        </div>
      </div>
      
      {/* Initial Risk Assessment (Justification) */}
      <div>
        <div className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-800 text-xs font-semibold mb-2">
          Initial Risk Assessment
        </div>
        <div className="border border-slate-200 rounded-md p-4 bg-slate-50 text-sm text-slate-700">
          {risk.justification || 'No justification provided.'}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessmentPanel;
