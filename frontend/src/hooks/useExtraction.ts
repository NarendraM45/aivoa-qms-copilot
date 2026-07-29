import { useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { useExtractFromFileMutation, useExtractFromTextMutation } from '../store/api';
import { setUploadState, setError, setRunId, setExtractionProgress, setCurrentNode } from '../store/aiPanelSlice';
import { loadFromExtraction } from '../store/complaintFormSlice';

/**
 * Custom hook for triggering AI extraction via HTTP endpoints.
 * 
 * Two modes:
 * - uploadFile: Send a file to /extract/upload (for PDF/DOCX/TXT/EML)
 * - pasteText: Send raw text to /extract/text
 * 
 * Both return the full extraction result synchronously.
 * For real-time progress, use the WebSocket flow instead.
 */
export function useExtraction() {
  const dispatch = useDispatch();
  const [extractFile, { isLoading: isFileLoading }] = useExtractFromFileMutation();
  const [extractText, { isLoading: isTextLoading }] = useExtractFromTextMutation();

  const processResult = useCallback((res: any) => {
    // Convert field_confidence array to a lookup map
    const confidenceMap: Record<string, number> = {};
    if (Array.isArray(res.field_confidence)) {
      for (const fc of res.field_confidence) {
        if (fc.field_name && fc.confidence !== undefined) {
          confidenceMap[fc.field_name] = fc.confidence;
        }
      }
    }

    dispatch(loadFromExtraction({
      extractedFields: res.extracted_fields || {},
      confidenceScores: confidenceMap,
    }));
    dispatch(setRunId(res.run_id));
    dispatch(setExtractionProgress(100));
    dispatch(setCurrentNode('Extraction complete'));
    dispatch(setUploadState('complete'));
  }, [dispatch]);

  const uploadFile = useCallback(async (file: File) => {
    dispatch(setUploadState('uploading'));
    dispatch(setError(null));
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await extractFile(formData).unwrap();
      processResult(res);
    } catch (err: any) {
      dispatch(setUploadState('error'));
      dispatch(setError(err?.data?.detail || 'Failed to upload file'));
    }
  }, [dispatch, extractFile, processResult]);

  const pasteText = useCallback(async (text: string) => {
    dispatch(setUploadState('uploading'));
    dispatch(setError(null));
    try {
      // Backend expects { raw_text: string }
      const res = await extractText({ raw_text: text }).unwrap();
      processResult(res);
    } catch (err: any) {
      dispatch(setUploadState('error'));
      dispatch(setError(err?.data?.detail || 'Failed to process text'));
    }
  }, [dispatch, extractText, processResult]);

  return { uploadFile, pasteText, isLoading: isFileLoading || isTextLoading };
}
