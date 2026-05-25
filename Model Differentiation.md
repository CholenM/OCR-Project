| Model | Role in Pipeline | Why Chosen | Strengths | Tradeoffs |
| --- | --- | --- | --- | --- |
| Qwen3-VL-8B-Instruct_Q4_K_M | Early OCR/vision model candidate | Strong multilingual reasoning and doc understanding | Good generalization, solid layout understanding | Heavier, slower; overkill for pure OCR |
| PaddleOCR-1.5B_F16 | Primary OCR engine choice | Fast, accurate text extraction with strong table support | High accuracy on printed text, good table reconstruction | Less semantic reasoning; needs layout handling elsewhere |
| LightOnOCR-1.5B_F16 | Final optimized OCR layer | Tuned for legal docs with speed/cost focus | Consistent output, faster throughput, cost-efficient | Narrower scope; relies on clean inputs |
