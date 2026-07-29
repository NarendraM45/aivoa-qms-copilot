import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { ComplaintFormState, ComplaintField } from '../types';

const initialField: ComplaintField = { value: null, source: null, confidence: null };

const initialState: ComplaintFormState = {
  complaintId: null,
  status: 'pending_triage',
  isSaving: false,
  saveError: null,
  complaint_source: initialField,
  customer_name: initialField,
  product_name: initialField,
  product_strength: initialField,
  batch_number: initialField,
  manufacturing_date: initialField,
  expiry_date: initialField,
  quantity_affected: initialField,
  quantity_unit: initialField,
  complaint_type: initialField,
  complaint_date: initialField,
  complaint_description: initialField,
  initial_severity: initialField,
  priority: initialField,
};

const complaintFormSlice = createSlice({
  name: 'complaintForm',
  initialState,
  reducers: {
    setField: (
      state,
      action: PayloadAction<{ field: keyof Omit<ComplaintFormState, 'complaintId' | 'status' | 'isSaving' | 'saveError'>; value: any; source: 'ai' | 'user' | null; confidence: number | null }>
    ) => {
      const { field, value, source, confidence } = action.payload;
      (state as any)[field] = { value, source, confidence };
    },
    resetForm: () => initialState,
    loadFromExtraction: (state, action: PayloadAction<{ extractedFields: any; confidenceScores: any }>) => {
      const { extractedFields, confidenceScores } = action.payload;
      Object.keys(extractedFields).forEach((key) => {
        if (key in state && !['complaintId', 'status', 'isSaving', 'saveError'].includes(key)) {
          (state as any)[key] = {
            value: extractedFields[key],
            source: 'ai',
            confidence: confidenceScores[key] || null,
          };
        }
      });
    },
    setStatus: (state, action: PayloadAction<string>) => {
      state.status = action.payload;
    },
    setComplaintId: (state, action: PayloadAction<string | null>) => {
      state.complaintId = action.payload;
    },
  },
});

export const { setField, resetForm, loadFromExtraction, setStatus, setComplaintId } = complaintFormSlice.actions;
export default complaintFormSlice.reducer;
