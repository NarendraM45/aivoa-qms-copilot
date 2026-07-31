import React, { useRef } from 'react';
import RiskAssessmentPanel from './RiskAssessment';
import AIAssistantChat from './AIAssistantChat';
import type { AIAssistantChatHandle } from './AIAssistantChat';
import CopilotFeatureBar from './CopilotFeatureBar';
import { Sparkles } from 'lucide-react';

const AIAssistantPanel: React.FC = () => {
  const chatRef = useRef<AIAssistantChatHandle>(null);

  const handleFeatureClick = (prompt: string, _label: string) => {
    chatRef.current?.sendMessage(prompt);
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Panel Header */}
      <div className="px-5 py-3.5 border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50 shrink-0">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Sparkles size={16} className="text-white" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-800">AIVOA Co-Pilot</h2>
            <p className="text-[11px] text-slate-500">AI-Powered Quality Assistant</p>
          </div>
        </div>
      </div>
      
      {/* Risk Assessment Section */}
      <div className="p-4 border-b border-slate-100 shrink-0">
        <RiskAssessmentPanel />
      </div>

      {/* Bonus Feature Buttons */}
      <CopilotFeatureBar
        onFeatureClick={handleFeatureClick}
        disabled={chatRef.current?.isProcessing}
      />
      
      {/* Chat Section — fills remaining space */}
      <div className="flex-1 min-h-0 flex flex-col">
        <AIAssistantChat ref={chatRef} />
      </div>
    </div>
  );
};

export default AIAssistantPanel;
