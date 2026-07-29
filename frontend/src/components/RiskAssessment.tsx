import React from 'react';
import { useSelector } from 'react-redux';
import type { RootState } from '../store';
import { ShieldAlert, ArrowRight, AlertTriangle, CheckCircle } from 'lucide-react';

const severityConfig: Record<string, { bg: string; text: string; border: string; label: string }> = {
  critical: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', label: 'Critical' },
  major: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', label: 'Major' },
  minor: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', label: 'Minor' },
};

const priorityConfig: Record<string, { bg: string; text: string }> = {
  urgent: { bg: 'bg-red-100', text: 'text-red-800' },
  high: { bg: 'bg-orange-100', text: 'text-orange-800' },
  medium: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
  low: { bg: 'bg-slate-100', text: 'text-slate-700' },
};

const RiskAssessmentPanel: React.FC = () => {
  const risk = useSelector((state: RootState) => state.aiPanel.riskAssessment);
  
  const hasSomething = risk.severity || risk.priority || risk.nextAction || risk.justification;
  
  if (!hasSomething) {
    return (
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <ShieldAlert size={16} className="text-slate-400" />
          <h3 className="text-sm font-semibold text-slate-500">AI Co-Pilot Risk Assessment</h3>
        </div>
        <p className="text-xs text-slate-400 italic">
          Describe a complaint in the chat below, and the AI will assess the risk here.
        </p>
      </div>
    );
  }
  
  const sev = risk.severity ? severityConfig[risk.severity] || severityConfig.minor : null;
  const pri = risk.priority ? priorityConfig[risk.priority] || priorityConfig.low : null;
  
  return (
    <div className={`p-4 border rounded-lg ${sev ? sev.bg : 'bg-slate-50'} ${sev ? sev.border : 'border-slate-200'}`}>
      <div className="flex items-center gap-2 mb-3">
        <ShieldAlert size={16} className={sev ? sev.text : 'text-slate-500'} />
        <h3 className="text-sm font-semibold text-slate-700">AI Co-Pilot Risk Assessment</h3>
      </div>
      
      {/* Severity & Priority Badges */}
      <div className="flex flex-wrap gap-2 mb-3">
        {sev && (
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold ${sev.bg} ${sev.text} border ${sev.border}`}>
            {risk.severity === 'critical' ? <AlertTriangle size={12} /> : risk.severity === 'minor' ? <CheckCircle size={12} /> : <ShieldAlert size={12} />}
            Severity: {sev.label}
          </span>
        )}
        {pri && (
          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${pri.bg} ${pri.text}`}>
            Priority: {risk.priority?.charAt(0).toUpperCase()}{risk.priority?.slice(1)}
          </span>
        )}
      </div>
      
      {/* Next Action */}
      {risk.nextAction && (
        <div className="flex items-start gap-2 mb-3 p-2.5 bg-white/70 rounded-md border border-slate-200">
          <ArrowRight size={14} className="text-blue-500 mt-0.5 shrink-0" />
          <div>
            <p className="text-xs font-bold text-slate-500 uppercase mb-0.5">Recommended Action</p>
            <p className="text-sm text-slate-700">{risk.nextAction}</p>
          </div>
        </div>
      )}
      
      {/* Justification */}
      {risk.justification && (
        <p className="text-xs text-slate-600 leading-relaxed mb-2">
          <span className="font-semibold">Justification:</span> {risk.justification}
        </p>
      )}
      
      {/* Risk Factors */}
      {risk.riskFactors.length > 0 && (
        <div className="mt-2">
          <p className="text-xs font-bold text-slate-500 uppercase mb-1">Risk Factors</p>
          <div className="flex flex-wrap gap-1.5">
            {risk.riskFactors.map((factor, i) => (
              <span key={i} className="text-xs px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-600">
                {factor}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskAssessmentPanel;
