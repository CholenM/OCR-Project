# Experimental OCR API Pipeline

## Overview
An API-Driven Optical Character Recognition (OCR) System designed to process complex documents (PDFs, JPGs, PNGs) and output structured Markdown (.md). This project is **Highly Experimental** and specifically optimized for high throughput on Apple Silicon (Metal Framework).

## Architecture
* **Core Model:** Qwen3-VL-2B-Instructed-GGUF *Stable* & PaddleOCR-VL-1.5 *Fast but no formatting* & LightOnOCR-1.5 *Reliable So Far (Fast and Accurate)*
* **API Framework:** FastAPI
* **Processing Stategy:** Chunk-by-Chunk / Page-by-page inference to ensure stability and future-proof pipeline.

## Current Status
* [x] Multi-format support (PDF, JPG, PNG)
* [x] Markdown format output extraction
* [x] API Key authentication implemented
* [x] Table and complex font recognition *depends on the LLM used*
* [ ] Multi-Token Prediction (MTP) integration (Exploring)

## Experimentation Log

### Benchmark 1: Context Size vs Throughput
* **Hardware:** Mac Mini M4 Pro
* **Setup:** Qwen3-VL-2B-Instruct & Context Size 8000 vs 16,000
* **Result:** 800 context yielded ~230 tokens/sec. Increasing to 16,000 context reduced throughput to ~184 tokens/sec.
* **Note:** Extraction DPI Heavily impacts processing speed

### Benchmark 2: Processing Strategy
* **Setup:** Qwen3-VL-2B-Instruct & Context Size 8000 vs 16,000
* **Setup:** Full document processing vs. Chunk-by-chunk processing.
* **Result:** Chunk processing (page-by-page) adopted. Bypasses memory bottlenecks and prevents hallucination drift associated with larger context windows. 

### Benchmark 3: Model Change
* **Setup:** Changed to PaddleOCR-VL-1.5
* **Result:** Generated a throughput of ~430 tokens/sec. But it doesnt generate a proper markdown for tables which is the only trade off by gaining a much accurate result.