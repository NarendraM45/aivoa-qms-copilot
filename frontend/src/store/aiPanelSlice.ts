import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { AIPanelState, ChatMessage, RiskAssessment } from '../types';

const initialRiskAssessment: RiskAssessment = {
  severity: null,
  priority: null,
  nextAction: null,
  justification: null,
  riskFactors: [],
};

const initialState: AIPanelState = {
  uploadState: 'idle',
  extractionProgress: 0,
  currentNode: '',
  chatMessages: [],
  error: null,
  runId: null,
  riskAssessment: initialRiskAssessment,
};

const aiPanelSlice = createSlice({
  name: 'aiPanel',
  initialState,
  reducers: {
    setUploadState: (state, action: PayloadAction<AIPanelState['uploadState']>) => {
      state.uploadState = action.payload;
    },
    setExtractionProgress: (state, action: PayloadAction<number>) => {
      state.extractionProgress = action.payload;
    },
    setCurrentNode: (state, action: PayloadAction<string>) => {
      state.currentNode = action.payload;
    },
    addChatMessage: (state, action: PayloadAction<ChatMessage>) => {
      state.chatMessages.push(action.payload);
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setRunId: (state, action: PayloadAction<string | null>) => {
      state.runId = action.payload;
    },
    setRiskAssessment: (state, action: PayloadAction<Partial<RiskAssessment>>) => {
      state.riskAssessment = { ...state.riskAssessment, ...action.payload };
    },
    resetRiskAssessment: (state) => {
      state.riskAssessment = initialRiskAssessment;
    },
    resetAIPanel: () => initialState,
  },
});

export const {
  setUploadState,
  setExtractionProgress,
  setCurrentNode,
  addChatMessage,
  setError,
  setRunId,
  setRiskAssessment,
  resetRiskAssessment,
  resetAIPanel,
} = aiPanelSlice.actions;
export default aiPanelSlice.reducer;
