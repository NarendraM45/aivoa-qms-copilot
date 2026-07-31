import React from 'react';
import { 
  ClipboardCheck, 
  GitFork, 
  Copy, 
  ShieldCheck, 
  FileText, 
  AlertTriangle 
} from 'lucide-react';

interface FeatureButton {
  id: string;
  label: string;
  icon: React.ReactNode;
  prompt: string;
  color: string;
}

const features: FeatureButton[] = [
  {
    id: 'completeness',
    label: 'Completeness',
    icon: <ClipboardCheck size={13} />,
    prompt: 'Check the current complaint form for completeness. Which fields are filled, which are missing, and what is the overall completeness percentage?',
    color: 'text-emerald-600 bg-emerald-50 border-emerald-200 hover:bg-emerald-100',
  },
  {
    id: 'root-cause',
    label: 'Root Cause',
    icon: <GitFork size={13} />,
    prompt: 'Perform an Ishikawa root cause analysis for this complaint. Consider Man, Machine, Method, Material, Measurement, and Environment factors.',
    color: 'text-violet-600 bg-violet-50 border-violet-200 hover:bg-violet-100',
  },
  {
    id: 'duplicates',
    label: 'Duplicates',
    icon: <Copy size={13} />,
    prompt: 'Check if this complaint could be a duplicate. Analyze the product, batch number, and complaint pattern for similarities with potential prior reports.',
    color: 'text-amber-600 bg-amber-50 border-amber-200 hover:bg-amber-100',
  },
  {
    id: 'capa',
    label: 'CAPA',
    icon: <ShieldCheck size={13} />,
    prompt: 'Recommend CAPA (Corrective and Preventive Actions) for this complaint. Separate corrective actions from preventive actions and reference applicable pharma standards.',
    color: 'text-blue-600 bg-blue-50 border-blue-200 hover:bg-blue-100',
  },
  {
    id: 'summary',
    label: 'Summary',
    icon: <FileText size={13} />,
    prompt: 'Generate a concise management-ready summary of this complaint for QA leadership review.',
    color: 'text-slate-600 bg-slate-50 border-slate-200 hover:bg-slate-100',
  },
  {
    id: 'risk',
    label: 'Risk Class.',
    icon: <AlertTriangle size={13} />,
    prompt: 'Perform a detailed AI risk classification covering Patient Safety, Regulatory Impact, Business Impact, and Supply Chain Impact. Rate each factor and provide an overall risk score.',
    color: 'text-rose-600 bg-rose-50 border-rose-200 hover:bg-rose-100',
  },
];

interface Props {
  onFeatureClick: (prompt: string, label: string) => void;
  disabled?: boolean;
}

const CopilotFeatureBar: React.FC<Props> = ({ onFeatureClick, disabled }) => {
  return (
    <div className="px-3 py-2 border-b border-slate-100 shrink-0">
      <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5 px-1">AI Analysis Tools</p>
      <div className="flex flex-wrap gap-1.5">
        {features.map((f) => (
          <button
            key={f.id}
            onClick={() => onFeatureClick(f.prompt, f.label)}
            disabled={disabled}
            className={`inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border text-[11px] font-medium transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed ${f.color}`}
            title={f.prompt}
          >
            {f.icon}
            {f.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default CopilotFeatureBar;
