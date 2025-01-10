# RAG_APIDoc_Dev_Guide

Key components:

APIDocCrawler: Recursively crawls API documentation using LangChain's RecursiveUrlLoader
RAGStore: Manages vector embeddings using HuggingFace models and Chroma vector store
APIIntegration: Main interface for the RAG system

To use:

Initialize APIIntegration with target API URL
Call initialize() to crawl and create vector store
Use get_api_info() or generate_code_snippet() for retrieving information
