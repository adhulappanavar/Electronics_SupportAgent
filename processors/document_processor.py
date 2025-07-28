import os
import uuid
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path
import PyPDF2
from docx import Document
import json
from config import CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_EXTENSIONS

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = CHUNK_SIZE
        self.chunk_overlap = CHUNK_OVERLAP
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.txt' or file_extension == '.md':
            return self._extract_from_text(file_path)
        elif file_extension == '.pdf':
            return self._extract_from_pdf(file_path)
        elif file_extension == '.docx':
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_text(self, file_path: str) -> str:
        """Extract text from txt/md files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk = " ".join(chunk_words)
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def process_document(self, file_path: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a document and return chunks with metadata"""
        try:
            # Extract text
            text = self.extract_text_from_file(file_path)
            
            # Split into chunks
            chunks = self.chunk_text(text)
            
            # Create document objects
            documents = []
            file_name = Path(file_path).name
            
            for i, chunk in enumerate(chunks):
                doc = {
                    'id': str(uuid.uuid4()),
                    'content': chunk,
                    'file_name': file_name,
                    'chunk_index': i,
                    'brand': metadata.get('brand', ''),
                    'product_category': metadata.get('product_category', ''),
                    'document_type': metadata.get('document_type', ''),
                    'metadata': {
                        'original_file': file_path,
                        'total_chunks': len(chunks),
                        **metadata
                    }
                }
                documents.append(doc)
            
            return documents
        
        except Exception as e:
            print(f"Error processing document {file_path}: {e}")
            return []
    
    def process_directory(self, directory_path: str, default_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Process all supported files in a directory"""
        all_documents = []
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            print(f"Directory does not exist: {directory_path}")
            return []
        
        for file_path in directory_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                # Try to extract metadata from file path/name
                metadata = self._extract_metadata_from_path(file_path)
                if default_metadata:
                    metadata.update(default_metadata)
                
                documents = self.process_document(str(file_path), metadata)
                all_documents.extend(documents)
        
        return all_documents
    
    def _extract_metadata_from_path(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file path and name"""
        metadata = {}
        
        # Extract from file name patterns
        file_name = file_path.stem.lower()
        path_parts = [part.lower() for part in file_path.parts]
        
        # Brand detection
        if any('samsung' in part for part in path_parts + [file_name]):
            metadata['brand'] = 'Samsung'
        elif any('lg' in part for part in path_parts + [file_name]):
            metadata['brand'] = 'LG'
        
        # Product category detection
        if any('tv' in part for part in path_parts + [file_name]):
            metadata['product_category'] = 'TV'
        elif any('refrigerator' in part or 'fridge' in part for part in path_parts + [file_name]):
            metadata['product_category'] = 'Refrigerator'
        elif any('washing' in part or 'washer' in part for part in path_parts + [file_name]):
            metadata['product_category'] = 'Washing Machine'
        elif any('speaker' in part or 'audio' in part for part in path_parts + [file_name]):
            metadata['product_category'] = 'Speaker'
        elif any('ac' in part or 'air' in part for part in path_parts + [file_name]):
            metadata['product_category'] = 'Air Conditioner'
        
        # Document type detection
        if any('sop' in part or 'procedure' in part for part in path_parts + [file_name]):
            metadata['document_type'] = 'SOP'
        elif any('faq' in part for part in path_parts + [file_name]):
            metadata['document_type'] = 'FAQ'
        elif any('manual' in part for part in path_parts + [file_name]):
            metadata['document_type'] = 'User Manual'
        elif any('troubleshoot' in part for part in path_parts + [file_name]):
            metadata['document_type'] = 'Troubleshooting Guide'
        
        return metadata 