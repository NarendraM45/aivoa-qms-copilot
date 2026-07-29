export interface ComplaintField<T = any> {
  value: T | null;
  source: 'ai' | 'user' | null;
  confidence: number | null;
}

export interface ComplaintFormState {
  complaintId: string | null;
  status: string;
  isSaving: boolean;
  saveError: string | null;
  
  complaint_source: ComplaintField<string>;
  customer_name: ComplaintField<string>;
  product_name: ComplaintField<string>;
  product_strength: ComplaintField<string>;
  batch_number: ComplaintField<string>;
  manufacturing_date: ComplaintField<string>;
  expiry_date: ComplaintField<string>;
  quantity_affected: ComplaintField<number>;
  quantity_unit: ComplaintField<string>;
  complaint_type: ComplaintField<string>;
  complaint_date: ComplaintField<string>;
  complaint_description: ComplaintField<string>;
  initial_severity: ComplaintField<string>;
  priority: ComplaintField<string>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  message: string;
  timestamp: string;
  hasFile?: boolean;
  fileName?: string;
}

export interface RiskAssessment {
  severity: string | null;       // "minor" | "major" | "critical"
  priority: string | null;       // "low" | "medium" | "high" | "urgent"
  nextAction: string | null;
  justification: string | null;
  riskFactors: string[];
}

export interface AIPanelState {
  uploadState: 'idle' | 'uploading' | 'extracting' | 'complete' | 'error';
  extractionProgress: number;
  currentNode: string;
  chatMessages: ChatMessage[];
  error: string | null;
  runId: string | null;
  riskAssessment: RiskAssessment;
}
