import React from 'react';

interface RootCause {
  root_cause_category: string;
  root_cause_text: string;
  ai_confidence: string | number;
}

interface Props {
  data: RootCause[];
}

const categoryColors: Record<string, { bg: string; text: string }> = {
  Man: { bg: 'bg-blue-100', text: 'text-blue-700' },
  Machine: { bg: 'bg-purple-100', text: 'text-purple-700' },
  Method: { bg: 'bg-amber-100', text: 'text-amber-700' },
  Material: { bg: 'bg-red-100', text: 'text-red-700' },
  Environment: { bg: 'bg-green-100', text: 'text-green-700' },
  Measurement: { bg: 'bg-teal-100', text: 'text-teal-700' },
};

const RootCauseResults: React.FC<Props> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="mt-4 p-4 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 text-sm">
        No root cause suggestions available.
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-3">
      <p className="text-sm font-medium text-slate-700">
        Ishikawa/Fishbone Analysis — {data.length} potential root cause{data.length > 1 ? 's' : ''}:
      </p>
      {data.map((rc, idx) => {
        const colors = categoryColors[rc.root_cause_category] || { bg: 'bg-slate-100', text: 'text-slate-700' };
        const confidence = typeof rc.ai_confidence === 'string' ? parseFloat(rc.ai_confidence) : rc.ai_confidence;
        return (
          <div key={idx} className="p-4 bg-white border border-slate-200 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${colors.bg} ${colors.text}`}>
                {rc.root_cause_category}
              </span>
              {!isNaN(confidence) && (
                <span className="text-xs text-slate-500">
                  Confidence: {(confidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <p className="text-sm text-slate-700 leading-relaxed">{rc.root_cause_text}</p>
          </div>
        );
      })}
      <p className="text-xs text-slate-400 italic">
        These are AI-suggested root causes for human review — not final determinations.
      </p>
    </div>
  );
};

export default RootCauseResults;
