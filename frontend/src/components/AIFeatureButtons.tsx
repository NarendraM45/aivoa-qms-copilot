import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { Copy, Activity, FileCheck, ShieldAlert, Loader2 } from 'lucide-react';
import type { RootState } from '../store';
import {
  useCheckDuplicatesMutation,
  useGetRootCauseSuggestionsMutation,
  useGetCAPARecommendationsMutation,
  useCheckCompletenessMutation,
} from '../store/api';
import DuplicateResults from './DuplicateResults';
import RootCauseResults from './RootCauseResults';
import CAPAResults from './CAPAResults';
import CompletenessResults from './CompletenessResults';

const AIFeatureButtons: React.FC = () => {
  const complaintId = useSelector((state: RootState) => state.complaintForm.complaintId);
  const [activeFeature, setActiveFeature] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [checkDuplicates] = useCheckDuplicatesMutation();
  const [getRootCause] = useGetRootCauseSuggestionsMutation();
  const [getCapa] = useGetCAPARecommendationsMutation();
  const [checkCompleteness] = useCheckCompletenessMutation();

  const features = [
    { id: 'duplicates', label: 'Check Duplicates', icon: Copy, color: 'text-purple-600', bg: 'bg-purple-100' },
    { id: 'rootcause', label: 'Root Cause Analysis', icon: Activity, color: 'text-amber-600', bg: 'bg-amber-100' },
    { id: 'capa', label: 'CAPA Recommendations', icon: ShieldAlert, color: 'text-blue-600', bg: 'bg-blue-100' },
    { id: 'completeness', label: 'Completeness Check', icon: FileCheck, color: 'text-green-600', bg: 'bg-green-100' },
  ];

  const handleFeatureClick = async (featureId: string) => {
    if (activeFeature === featureId) {
      setActiveFeature(null);
      return;
    }

    setActiveFeature(featureId);
    
    if (!complaintId) {
      setError('Please save the complaint first before running AI analysis.');
      return;
    }

    // Only fetch if we don't already have results
    if (results[featureId]) return;

    setLoading(featureId);
    setError(null);

    try {
      let data: any;
      switch (featureId) {
        case 'duplicates':
          data = await checkDuplicates(complaintId).unwrap();
          break;
        case 'rootcause':
          data = await getRootCause(complaintId).unwrap();
          break;
        case 'capa':
          data = await getCapa(complaintId).unwrap();
          break;
        case 'completeness':
          data = await checkCompleteness(complaintId).unwrap();
          break;
      }
      setResults(prev => ({ ...prev, [featureId]: data }));
    } catch (err: any) {
      setError(err?.data?.detail || `Failed to run ${featureId} analysis`);
    } finally {
      setLoading(null);
    }
  };

  const renderResults = () => {
    if (loading) {
      return (
        <div className="mt-4 p-6 bg-white border border-slate-200 rounded-lg shadow-sm flex items-center justify-center gap-3 text-slate-500">
          <Loader2 size={18} className="animate-spin" />
          <span className="text-sm">Analyzing...</span>
        </div>
      );
    }

    if (error) {
      return (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      );
    }

    if (!activeFeature || !results[activeFeature]) return null;

    switch (activeFeature) {
      case 'duplicates':
        return <DuplicateResults data={results.duplicates} />;
      case 'rootcause':
        return <RootCauseResults data={results.rootcause} />;
      case 'capa':
        return <CAPAResults data={results.capa} />;
      case 'completeness':
        return <CompletenessResults data={results.completeness} />;
      default:
        return null;
    }
  };

  return (
    <div className="mb-4">
      <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">AI Quality Insights</h3>
      <div className="grid grid-cols-2 gap-3">
        {features.map(f => (
          <button 
            key={f.id}
            onClick={() => handleFeatureClick(f.id)}
            disabled={loading !== null}
            className={`flex flex-col items-center justify-center p-4 rounded-lg border transition-all ${
              activeFeature === f.id 
                ? 'border-blue-500 bg-white shadow-md ring-1 ring-blue-200' 
                : 'border-slate-200 bg-white hover:bg-slate-50 hover:shadow-sm'
            } disabled:opacity-50`}
          >
            <div className={`p-2 rounded-full mb-2 ${f.bg} ${f.color}`}>
              {loading === f.id ? <Loader2 size={20} className="animate-spin" /> : <f.icon size={20} />}
            </div>
            <span className="text-xs font-semibold text-slate-700 text-center leading-tight">{f.label}</span>
          </button>
        ))}
      </div>
      
      {renderResults()}
    </div>
  );
};

export default AIFeatureButtons;
