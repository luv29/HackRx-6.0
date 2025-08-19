import { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [jsonQuery, setJsonQuery] = useState('')
  const [results, setResults] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    try {
      // Parse JSON query to validate it
      const parsedQuery = JSON.parse(jsonQuery)
      
      // Make API call to backend
      const response = await fetch('http://localhost:8000/api/v1/hackrx/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          documents: url,
          questions: Array.isArray(parsedQuery) ? parsedQuery : [parsedQuery]
        })
      })
      
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Error:', error)
      setResults({ error: error.message })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="rag-container">
      <header className="rag-header">
        <div className="logo-container">
          <h1>RAG Assistant</h1>
          <div className="logo-badge">Retrieval Augmented Generation</div>
          <div className="logo-subtitle">~BOTS</div>
        </div>
      </header>
      
      <main className="rag-main">
        <h2 className="rag-title">Intelligent Document Retrieval</h2>
        <p className="rag-subtitle">
          Upload your queries as JSON and retrieve relevant information from any URL
          using advanced RAG technology
        </p>
        
        <div className="rag-content">
          <div className="input-section">
            <div className="input-header">
              <span className="input-icon">🌐</span>
              <h3>Input Configuration</h3>
            </div>
            <p>Provide a URL and upload your JSON query file</p>
            
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="targetUrl">Target URL</label>
                <input 
                  type="url" 
                  id="targetUrl"
                  placeholder="https://example.com/document"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="jsonQuery">Query JSON</label>
                <textarea
                  id="jsonQuery"
                  placeholder='Enter your JSON queries here (e.g. ["What is RAG?", "How does it work?"])'
                  value={jsonQuery}
                  onChange={(e) => setJsonQuery(e.target.value)}
                  required
                />
              </div>
              
              <button type="submit" className="submit-button" disabled={isLoading}>
                {isLoading ? 'Processing...' : 'Submit Query'}
              </button>
            </form>
          </div>
          
          <div className="results-section">
            <div className="results-header">
              <span className="results-icon">📄</span>
              <h3>Results</h3>
            </div>
            <p>Retrieved information will appear here</p>
            
            <div className="results-content">
              {isLoading ? (
                <p className="processing-message">Results will appear here after processing...</p>
              ) : results ? (
                results.error ? (
                  <div className="error-message">
                    <h4>Error</h4>
                    <p>{results.error}</p>
                  </div>
                ) : (
                  <div className="results-data">
                    {results.answers && results.answers.map((answer, index) => (
                      <div key={index} className="answer-item">
                        <h4>Answer {index + 1}</h4>
                        <p>{answer}</p>
                      </div>
                    ))}
                  </div>
                )
              ) : (
                <p className="empty-results">Results will appear here after processing...</p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
