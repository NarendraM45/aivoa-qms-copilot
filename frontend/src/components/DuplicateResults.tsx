import React from 'react';

interface Props {
  data: Array<{
    id?: string;
    potential_duplicate_id: string;
    similarity_score: number;
    match_reason: string;
  }>;
}

const DuplicateResults: React.FC<Props> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
        ✓ No potential duplicates found. This complaint appears to be unique.
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-3">
      <p className="text-sm font-medium text-slate-700">
        Found {data.length} potential duplicate{data.length > 1 ? 's' : ''}:
      </p>
      {data.map((dup, idx) => (
        <div key={dup.id || idx} className="p-4 bg-white border border-purple-200 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-slate-500">
              ID: {dup.potential_duplicate_id.slice(0, 8)}...
            </span>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              dup.similarity_score >= 0.8 ? 'bg-red-100 text-red-700' :
              dup.similarity_score >= 0.5 ? 'bg-amber-100 text-amber-700' :
              'bg-slate-100 text-slate-600'
            }`}>
              {(dup.similarity_score * 100).toFixed(0)}% match
            </span>
          </div>
          <div className="w-full bg-slate-200 rounded-full h-1.5 mb-2">
            <div
              className={`h-1.5 rounded-full transition-all ${
                dup.similarity_score >= 0.8 ? 'bg-red-500' :
                dup.similarity_score >= 0.5 ? 'bg-amber-500' : 'bg-slate-400'
              }`}
              style={{ width: `${dup.similarity_score * 100}%` }}
            />
          </div>
          <p className="text-sm text-slate-600">{dup.match_reason}</p>
        </div>
      ))}
    </div>
  );
};

export default DuplicateResults;
