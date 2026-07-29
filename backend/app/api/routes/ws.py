"""WebSocket endpoint for real-time extraction progress streaming."""
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.agents.graph import run_extraction

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/extraction/{run_id}")
async def extraction_websocket(websocket: WebSocket, run_id: str):
    """WebSocket endpoint that streams extraction progress in real time.
    
    Protocol:
    1. Client connects to /ws/extraction/{run_id}
    2. Client sends initial message: {"raw_text": "...", "source_file_type": "txt"}
    3. Server streams progress events: {"node": "...", "progress_pct": N, "message": "..."}
    4. Final message includes extracted_fields and field_confidence
    5. Server closes connection
    """
    await websocket.accept()
    try:
        # Receive the raw text from the client
        data = await websocket.receive_text()
        msg = json.loads(data)
        raw_text = msg.get("raw_text", "")
        source_file_type = msg.get("source_file_type", "txt")

        if not raw_text.strip():
            await websocket.send_json({"error": "raw_text cannot be empty"})
            return

        # Node-to-human-readable message mapping
        node_messages = {
            "parse_document": "Parsing document...",
            "extract_fields": "Extracting complaint fields...",
            "check_completeness": "Checking field completeness...",
            "classify_severity": "Classifying severity...",
            "detect_duplicates": "Detecting potential duplicates...",
            "generate_summary": "Generating summary...",
        }

        async def progress_callback(update_dict):
            """Send progress updates through WebSocket."""
            node = update_dict.get("node", "")
            message = node_messages.get(node, f"Processing {node}...")
            try:
                await websocket.send_json({
                    "node": node,
                    "progress_pct": update_dict.get("progress_pct", 0),
                    "message": message,
                })
            except Exception as e:
                logger.warning(f"Failed to send WS progress for {node}: {e}")

        # Run the extraction graph with progress callback
        final_state = await run_extraction(
            raw_text, source_file_type, run_id, progress_callback=progress_callback
        )

        # Send final result
        if final_state.get("errors"):
            await websocket.send_json({
                "node": "error",
                "progress_pct": 100,
                "message": "Extraction completed with errors",
                "errors": final_state["errors"],
                "extracted_fields": final_state.get("extracted_fields"),
                "field_confidence": final_state.get("field_confidence"),
            })
        else:
            await websocket.send_json({
                "node": "done",
                "progress_pct": 100,
                "message": "Extraction complete!",
                "extracted_fields": final_state.get("extracted_fields"),
                "field_confidence": final_state.get("field_confidence"),
                "missing_fields": final_state.get("missing_fields"),
                "completeness_score": final_state.get("completeness_score"),
                "severity_classification": final_state.get("severity_classification"),
                "summary": final_state.get("summary"),
                "duplicate_candidates": final_state.get("duplicate_candidates"),
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for run {run_id}")
    except json.JSONDecodeError:
        try:
            await websocket.send_json({"error": "Invalid JSON in initial message"})
        except Exception:
            pass
    except Exception as e:
        logger.error(f"WebSocket error for run {run_id}: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
