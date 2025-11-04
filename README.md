# DC Witness Research Tool

A Streamlit-based research tool that allows users to upload documents (PDFs, text files, CSVs) or URLs and ask questions using AI-powered retrieval and question answering.

## Features

- 📄 Upload multiple document types (PDF, TXT, CSV)
- 🌐 Process content from URLs
- 💬 Interactive chat interface
- 🔍 AI-powered question answering with source citations
- 🎨 Custom branded UI with DC Witness logo

## Local Development

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.streamlit/secrets.toml` and add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

4. Run the app:
   ```bash
   streamlit run main.py
   ```

## Deployment on Streamlit Cloud

This app is configured for easy deployment on Streamlit Cloud:

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Add your `OPENAI_API_KEY` in the Secrets section
6. Deploy!

## Usage

1. **Add Documents**: Click "Add Documents" to upload files or enter URLs
2. **Process**: Click "Process Documents" to index your content
3. **Ask Questions**: Use the chat interface to ask questions about your documents
4. **View Sources**: Expand the "Sources" section to see where answers came from

## Technology Stack

- **Streamlit**: Web application framework
- **LangChain**: Document processing and Q&A chains
- **OpenAI**: Embeddings and language model
- **FAISS**: Vector similarity search

## License

Proprietary - DC Witness

## Support

For questions or issues, contact your development team.

