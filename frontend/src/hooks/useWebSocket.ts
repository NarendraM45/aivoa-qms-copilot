import { useEffect, useRef, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { setExtractionProgress, setCurrentNode, setUploadState, setError } from '../store/aiPanelSlice';
import { loadFromExtraction } from '../store/complaintFormSlice';

/**
 * Custom hook for WebSocket connection to the extraction progress endpoint.
 * 
 * The protocol:
 * 1. Client connects to /ws/extraction/{runId}
 * 2. Client sends: { "raw_text": "...", "source_file_type": "txt" }
 * 3. Server streams: { "node": "...", "progress_pct": N, "message": "..." }
 * 4. Final message has node="done" with extracted_fields + field_confidence
 */
export function useWebSocket(runId: string | null) {
  const dispatch = useDispatch();
  const wsRef = useRef<WebSocket | null>(null);

  const sendMessage = useCallback((data: { raw_text: string; source_file_type?: string }) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    if (!runId) return;

    const wsUrl = `${import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'}/ws/extraction/${runId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      dispatch(setUploadState('extracting'));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Check for errors
        if (data.error) {
          dispatch(setError(typeof data.error === 'string' ? data.error : JSON.stringify(data.error)));
          dispatch(setUploadState('error'));
          return;
        }

        // Progress update or final result — backend sends { node, progress_pct, message }
        if (data.progress_pct !== undefined) {
          dispatch(setExtractionProgress(data.progress_pct));
        }
        if (data.node) {
          dispatch(setCurrentNode(data.message || data.node));
        }

        // Final extraction result — node is "done"
        if (data.node === 'done' && data.extracted_fields) {
          // Convert field_confidence array to a lookup map { field_name: confidence }
          const confidenceMap: Record<string, number> = {};
          if (Array.isArray(data.field_confidence)) {
            for (const fc of data.field_confidence) {
              if (fc.field_name && fc.confidence !== undefined) {
                confidenceMap[fc.field_name] = fc.confidence;
              }
            }
          } else if (data.field_confidence && typeof data.field_confidence === 'object') {
            Object.assign(confidenceMap, data.field_confidence);
          }

          dispatch(loadFromExtraction({
            extractedFields: data.extracted_fields,
            confidenceScores: confidenceMap,
          }));
          dispatch(setUploadState('complete'));
          dispatch(setExtractionProgress(100));
          dispatch(setCurrentNode('Extraction complete'));
        }
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    ws.onerror = () => {
      dispatch(setUploadState('error'));
      dispatch(setError('WebSocket connection error'));
    };

    ws.onclose = () => {
      wsRef.current = null;
    };

    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [runId, dispatch]);

  return { sendMessage, ws: wsRef };
}
