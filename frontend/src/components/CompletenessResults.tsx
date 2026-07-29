import React from 'react';

interface Props {
  data: {
    completeness_score: number;
    missing_fields: string[];
    suggestions?: Record<string, string>;
  };
}

const fieldLabels: Record<string, string> = {
  product_name: 'Product Name',
  batch_number: 'Batch/Lot Number',
  complaint_description: 'Complaint Description',
  complaint_type: 'Complaint Type',
  complaint_date: 'Complaint Date',
  customer_name: 'Customer Name',
  complaint_source: 'Complaint Source',
  manufacturing_date: 'Manufacturing Date',
  expiry_date: 'Expiry Date',
};

const CompletenessResults: React.FC<Props> = ({ data }) => {
  if (!data) return null;

  const pct = Math.round(data.completeness_score * 100);
  const isComplete = data.missing_fields.length === 0;

  return (
    <div className="mt-4 space-y-3">
      <p className="text-sm font-medium text-slate-700">Completeness Check</p>

      {/* Score Ring */}
      <div className="flex items-center gap-4 p-4 bg-white border border-slate-200 rounded-lg">
        <div className="relative w-16 h-16">
          <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="#e2e8f0"
              strokeWidth="3"
            />
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke={pct >= 80 ? '#10b981' : pct >= 50 ? '#f59e0b' : '#ef4444'}
              strokeWidth="3"
              strokeDasharray={`${pct}, 100`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-sm font-bold ${
              pct >= 80 ? 'text-green-600' : pct >= 50 ? 'text-amber-600' : 'text-red-600'
            }`}>
              {pct}%
            </span>
          </div>
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-800">
            {isComplete ? 'All fields complete!' : `${data.missing_fields.length} field${data.missing_fields.length > 1 ? 's' : ''} missing`}
          </p>
          <p className="text-xs text-slate-500">
            {pct >= 80 ? 'Good — ready for triage' : pct >= 50 ? 'Partial — review needed' : 'Incomplete — critical fields missing'}
          </p>
        </div>
      </div>

      {/* Missing Fields */}
      {data.missing_fields.length > 0 && (
        <div className="space-y-2">
          {data.missing_fields.map((field) => (
            <div key={field} className="flex items-center gap-2 p-2 bg-amber-50 border border-amber-200 rounded-md">
              <span className="text-amber-500 text-xs">⚠</span>
              <span className="text-sm text-amber-800 font-medium">
                {fieldLabels[field] || field.replace(/_/g, ' ')}
              </span>
              {data.suggestions?.[field] && (
                <span className="text-xs text-amber-600 ml-auto">
                  {data.suggestions[field]}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CompletenessResults;
