# adobe-india-hackathon-1a

## 👨‍💻 Authors

This solution was developed by Team for Adobe India Hackathon 2024:

- **Tushar Chattarki**  
- **Sumit Pagar**  
- **Rishikesh More**

# 📄 PDF Outline Extractor – Challenge 1A | Adobe India Hackathon

This repository contains a robust solution for **Challenge 1A** of the Adobe India Hackathon:  
🔍 **Extracting structured outlines from PDF files (Title, H1, H2, H3) in under 10 seconds**.

---

## 🚀 Problem Statement

PDFs are designed for humans — not machines. Our task is to **extract a hierarchical outline** from a PDF file (up to 50 pages), including:

- ✅ Document Title  
- ✅ Headings: H1, H2, H3  
- ✅ Page numbers for each heading  

This outline will serve as the backbone for advanced use-cases such as semantic search and document understanding.

---

## 🎯 Constraints

- ⚡ Must execute within **10 seconds** for a 50-page PDF  
- ❌ No internet access or API calls allowed  
- 💻 Must run on **CPU-only** (amd64), on a system with **8 CPUs and 16GB RAM**  
- 📦 Model size (if any) must be **≤ 200MB**  
- ✅ Generalize across simple and complex PDFs  
- 🚫 No hardcoded rules per file — must be content-agnostic  

---

## 🧠 Approach

1. **PDF Parsing** – Using [PyMuPDF (fitz)] to extract text, font properties, and structure.
2. **Heading Detection** – Based on:
   - Font size clusters
   - Font weight/style
   - Positional hierarchy
   - Smart filtering of repetitive elements
3. **Title Detection** – From the first page using largest unique text, semantic cues.
4. **Hierarchical Structuring** – Classifying heading levels into H1, H2, H3 using learned patterns and font hierarchy.
5. **Output Formatting** – Clean, standardized JSON output matching spec.

---

## 📂 Input

- PDF file (max 50 pages)
  
```
bash
python extractor.py input.pdf --output output.json
