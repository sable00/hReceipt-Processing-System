import logging
import uuid
import asyncio # Needed for placeholder db storage simulation

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

# Import placeholder modules
from modules import ocr, embeddings, vector_db, parsing, extraction

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Invoice Processing System",
    description="Processes invoices using OCR, Multi-Modal Embeddings, and VLM Parsing.",
    version="0.1.0"
)

@app.post("/processInvoice", tags=["Invoice Processing"])
async def process_invoice_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to upload an invoice (image/PDF) and process it.

    - Performs OCR.
    - Generates Multi-Modal Embeddings.
    - Stores embeddings in Vector DB (placeholder).
    - Parses invoice using VLM/DocLing (placeholder).
    - Extracts structured data.
    """
    logging.info(f"Received file: {file.filename}, content type: {file.content_type}")

    # Ensure file is provided
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    # Generate a unique ID for this document processing task
    doc_id = str(uuid.uuid4())
    logging.info(f"Processing document with ID: {doc_id}")

    try:
        # Read file content
        file_content = await file.read()
        if not file_content:
             raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # --- Workflow Steps ---

        # 1. OCR: Extracts text from invoices.
        logging.info(f"[{doc_id}] Step 1: Performing OCR...")
        extracted_text = await ocr.perform_ocr(file_content)
        logging.info(f"[{doc_id}] OCR Result (preview): {extracted_text[:100]}...") # Log preview

        # 2. Generate Multi-Modal Embeddings: Creates embeddings for invoices.
        logging.info(f"[{doc_id}] Step 2: Generating Embeddings...")
        invoice_embedding = await embeddings.generate_multi_modal_embeddings(
            text_content=extracted_text,
            file_content=file_content # Pass image bytes for multi-modal aspect
        )
        logging.info(f"[{doc_id}] Embedding generated (size: {len(invoice_embedding)}).")

        # 3. Vector DB (Elasticsearch): Stores embeddings and document IDs.
        logging.info(f"[{doc_id}] Step 3: Storing Embedding in Vector DB...")
        # You might extract some metadata from parsing later, or pass basic info now
        await vector_db.store_embedding(doc_id=doc_id, embedding=invoice_embedding)
        logging.info(f"[{doc_id}] Embedding stored.")

        # 4. Invoice Parsing: Uses VLM/DocLing for parsing.
        logging.info(f"[{doc_id}] Step 4: Parsing Invoice...")
        # Parsing might need text, original image, or maybe even embeddings depending on the model
        parsed_result = await parsing.parse_invoice_with_vlm(
            text_content=extracted_text,
            file_content=file_content
        )
        logging.info(f"[{doc_id}] Parsing completed.")
        # logging.debug(f"[{doc_id}] Raw Parsed Result: {parsed_result}") # More detailed log if needed

        # 5. Text Data Extraction: Extracts relevant data from the text/parsed result.
        logging.info(f"[{doc_id}] Step 5: Extracting Structured Data...")
        final_structured_data = await extraction.extract_structured_data(parsed_result)
        logging.info(f"[{doc_id}] Data Extraction completed.")

        # --- Process Completion ---
        logging.info(f"[{doc_id}] Invoice processing completed successfully.")
        return JSONResponse(content={
            "document_id": doc_id,
            "extracted_data": final_structured_data,
            "message": "Invoice processed successfully (using placeholders)."
        })

    except HTTPException as http_exc:
        # Re-raise FastAPI's HTTP exceptions
        raise http_exc
    except Exception as e:
        logging.exception(f"[{doc_id}] An error occurred during invoice processing: {e}") # Log traceback
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")
    finally:
        # Ensure file handle is closed if necessary (FastAPI usually handles this)
        await file.close()
        logging.info(f"[{doc_id}] File closed.")


@app.get("/", tags=["Health Check"])
async def read_root():
    """ Basic health check endpoint. """
    return {"status": "Invoice Processing API is running"}

# --- Running the App (for local development) ---
if __name__ == "__main__":
    import uvicorn
    # Host '0.0.0.0' makes it accessible on the network
    uvicorn.run(app, host="0.0.0.0", port=8000)