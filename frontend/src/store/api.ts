import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000' }),
  tagTypes: ['Complaint', 'AuditTrail', 'Chat'],
  endpoints: (builder) => ({
    getComplaints: builder.query({ query: (params) => ({ url: '/api/complaints', params }), providesTags: ['Complaint'] }),
    getComplaint: builder.query({ query: (id) => `/api/complaints/${id}`, providesTags: (_result, _error, id) => [{ type: 'Complaint', id }] }),
    createComplaint: builder.mutation({ query: (body) => ({ url: '/api/complaints', method: 'POST', body }), invalidatesTags: ['Complaint'] }),
    updateComplaint: builder.mutation({ query: ({ id, ...body }) => ({ url: `/api/complaints/${id}`, method: 'PUT', body }), invalidatesTags: (_result, _error, { id }) => [{ type: 'Complaint', id }] }),
    deleteComplaint: builder.mutation({ query: (id) => ({ url: `/api/complaints/${id}`, method: 'DELETE' }), invalidatesTags: ['Complaint'] }),
    
    extractFromFile: builder.mutation({ query: (formData) => ({ url: '/api/complaints/extract/upload', method: 'POST', body: formData }) }),
    extractFromText: builder.mutation({ query: (body) => ({ url: '/api/complaints/extract/text', method: 'POST', body }) }),
    
    sendChatMessage: builder.mutation({ query: ({ complaintId, message }) => ({ url: `/api/complaints/${complaintId}/chat`, method: 'POST', body: { message } }) }),
    getChatHistory: builder.query({ query: (complaintId) => `/api/complaints/${complaintId}/chat`, providesTags: ['Chat'] }),
    
    checkDuplicates: builder.mutation({ query: (id) => ({ url: `/api/complaints/${id}/check-duplicates`, method: 'POST' }) }),
    getRootCauseSuggestions: builder.mutation({ query: (id) => ({ url: `/api/complaints/${id}/root-cause-suggestions`, method: 'POST' }) }),
    getCAPARecommendations: builder.mutation({ query: (id) => ({ url: `/api/complaints/${id}/capa-recommendations`, method: 'POST' }) }),
    checkCompleteness: builder.mutation({ query: (id) => ({ url: `/api/complaints/${id}/completeness-check`, method: 'POST' }) }),
    getRiskClassification: builder.mutation({ query: (id) => ({ url: `/api/complaints/${id}/risk-classification`, method: 'POST' }) }),
    
    sendCopilotMessage: builder.mutation({
      query: (formData: FormData) => ({
        url: '/api/copilot/chat',
        method: 'POST',
        body: formData,
      }),
    }),
    
    getAuditTrail: builder.query({ query: (id) => `/api/complaints/${id}/audit-trail`, providesTags: ['AuditTrail'] }),
  }),
});

export const {
  useGetComplaintsQuery,
  useGetComplaintQuery,
  useCreateComplaintMutation,
  useUpdateComplaintMutation,
  useDeleteComplaintMutation,
  useExtractFromFileMutation,
  useExtractFromTextMutation,
  useSendChatMessageMutation,
  useGetChatHistoryQuery,
  useCheckDuplicatesMutation,
  useGetRootCauseSuggestionsMutation,
  useGetCAPARecommendationsMutation,
  useCheckCompletenessMutation,
  useGetRiskClassificationMutation,
  useSendCopilotMessageMutation,
  useGetAuditTrailQuery,
} = apiSlice;
