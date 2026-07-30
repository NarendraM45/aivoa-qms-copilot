import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../store';
import { useSendCopilotMessageMutation } from '../store/api';
import { addChatMessage, setRiskAssessment } from '../store/aiPanelSlice';
import { loadFromExtraction } from '../store/complaintFormSlice';
import { Send, Paperclip, X, FileText, Loader2, Bot, User } from 'lucide-react';

const AIAssistantChat: React.FC = () => {
  const dispatch = useDispatch();
  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const chatMessages = useSelector((state: RootState) => state.aiPanel.chatMessages);
  const formState = useSelector((state: RootState) => state.complaintForm);
  
  const [sendCopilot] = useSendCopilotMessageMutation();
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isProcessing]);
  
  const getCurrentFormValues = () => {
    const fields: Record<string, any> = {};
    const fieldNames = [
      'complaint_source', 'customer_name', 'product_name', 'product_strength',
      'batch_number', 'manufacturing_date', 'expiry_date', 'quantity_affected',
      'quantity_unit', 'complaint_type', 'complaint_date', 'complaint_description',
      'initial_severity', 'priority',
    ];
    for (const name of fieldNames) {
      const field = (formState as any)[name];
      if (field?.value != null && field.value !== '') {
        fields[name] = field.value;
      }
    }
    return fields;
  };
  
  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed && !selectedFile) return;
    
    // Add user message to chat
    const userMsg = {
      id: `msg-${Date.now()}`,
      role: 'user' as const,
      message: trimmed || `Uploaded: ${selectedFile?.name}`,
      timestamp: new Date().toISOString(),
      hasFile: !!selectedFile,
      fileName: selectedFile?.name,
    };
    dispatch(addChatMessage(userMsg));
    
    setInput('');
    setIsProcessing(true);
    
    try {
      // Build conversation history for context
      const history = chatMessages.map(m => ({
        role: m.role,
        content: m.message,
      }));
      
      // Build FormData (supports file upload)
      const formData = new FormData();
      formData.append('message', trimmed);
      formData.append('conversation_history', JSON.stringify(history));
      formData.append('current_form_state', JSON.stringify(getCurrentFormValues()));
      if (selectedFile) {
        formData.append('file', selectedFile);
      }
      
      const result = await sendCopilot(formData).unwrap();
      
      // Apply field updates to the complaint form
      if (result.field_updates && Object.keys(result.field_updates).length > 0) {
        // Build extraction data format for loadFromExtraction
        const extractedFields: Record<string, any> = {};
        const confidenceScores: Record<string, number> = {};
        
        for (const [key, value] of Object.entries(result.field_updates)) {
          extractedFields[key] = value;
          confidenceScores[key] = 0.9; // AI-populated fields get high confidence
        }
        
        dispatch(loadFromExtraction({ extractedFields, confidenceScores }));
      }
      
      // Apply risk assessment
      if (result.risk_assessment) {
        dispatch(setRiskAssessment({
          severity: result.risk_assessment.severity || null,
          priority: result.risk_assessment.priority || null,
          nextAction: result.risk_assessment.next_action || null,
          justification: result.risk_assessment.justification || null,
          riskFactors: result.risk_assessment.risk_factors || [],
        }));
      }
      
      // Add AI response to chat
      dispatch(addChatMessage({
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        message: result.message || 'Done.',
        timestamp: new Date().toISOString(),
      }));
      
    } catch (err: any) {
      const errorMsg = err?.data?.detail || err?.message || 'Failed to process request';
      dispatch(addChatMessage({
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        message: `⚠️ Error: ${errorMsg}`,
        timestamp: new Date().toISOString(),
      }));
    } finally {
      setIsProcessing(false);
      setSelectedFile(null);
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };
  
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };
  
  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {chatMessages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center opacity-60">
            <Bot size={40} className="text-slate-300 mb-3" />
            <p className="text-sm text-slate-500 font-medium">AIVOA Co-Pilot</p>
            <p className="text-xs text-slate-400 mt-1 max-w-[280px]">
              Describe a complaint, upload a document, or ask a question. I'll extract the details and populate the form automatically.
            </p>
            <div className="mt-4 space-y-1.5">
              <p className="text-[11px] text-slate-400 bg-slate-50 px-3 py-1.5 rounded-full">
                "Apollo Pharmacy reported discolored capsules in Amoxicylin 500mg..."
              </p>
              <p className="text-[11px] text-slate-400 bg-slate-50 px-3 py-1.5 rounded-full">
                "Sorry, batch number is BMX24602"
              </p>
              <p className="text-[11px] text-slate-400 bg-slate-50 px-3 py-1.5 rounded-full">
                📎 Upload a complaint PDF or email
              </p>
            </div>
          </div>
        )}
        
        {chatMessages.map((msg) => (
          <div key={msg.id} className={`flex gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                <Bot size={14} className="text-blue-600" />
              </div>
            )}
            <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
              msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-br-md' 
                : 'bg-slate-100 text-slate-800 rounded-bl-md'
            }`}>
              {msg.hasFile && (
                <div className={`flex items-center gap-1.5 mb-1.5 text-xs ${
                  msg.role === 'user' ? 'text-blue-200' : 'text-slate-500'
                }`}>
                  <FileText size={12} />
                  <span>{msg.fileName}</span>
                </div>
              )}
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.message}</p>
              <p className={`text-[10px] mt-1 ${
                msg.role === 'user' ? 'text-blue-300' : 'text-slate-400'
              }`}>
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 mt-0.5">
                <User size={14} className="text-slate-600" />
              </div>
            )}
          </div>
        ))}
        
        {/* Typing indicator */}
        {isProcessing && (
          <div className="flex gap-2.5 justify-start">
            <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <Bot size={14} className="text-blue-600" />
            </div>
            <div className="bg-slate-100 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex items-center gap-1.5">
                <Loader2 size={14} className="animate-spin text-blue-500" />
                <span className="text-sm text-slate-500">Analyzing...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* File attachment preview */}
      {selectedFile && (
        <div className="mx-4 mb-2 flex items-center gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg">
          <FileText size={14} className="text-blue-500" />
          <span className="text-xs text-blue-700 truncate flex-1">{selectedFile.name}</span>
          <button 
            onClick={() => setSelectedFile(null)}
            className="text-blue-400 hover:text-blue-600 transition-colors"
          >
            <X size={14} />
          </button>
        </div>
      )}
      
      {/* Input Bar */}
      <div className="p-3 border-t border-slate-200 bg-white">
        <div className="flex items-end gap-2">
          {/* File upload button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isProcessing}
            className="p-2 text-slate-400 hover:text-blue-500 hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
            title="Upload document (PDF, DOCX, TXT, EML)"
          >
            <Paperclip size={18} />
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.eml"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          {/* Text input */}
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe a complaint, correction, or ask a question..."
            disabled={isProcessing}
            rows={3}
            className="flex-1 resize-none rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none disabled:opacity-50 max-h-32 placeholder:text-slate-400"
            style={{ minHeight: '80px' }}
          />
          
          {/* Send button */}
          <button
            onClick={handleSend}
            disabled={isProcessing || (!input.trim() && !selectedFile)}
            className="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isProcessing ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistantChat;
