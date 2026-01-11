import React from 'react'

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({ error, errorInfo })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          padding: '40px', 
          background: '#09090b', 
          color: 'white', 
          minHeight: '100vh',
          fontFamily: 'monospace'
        }}>
          <h1 style={{ color: '#ef4444', fontSize: '32px', marginBottom: '20px' }}>
            ⚠️ Component Error Detected
          </h1>
          <div style={{ 
            background: '#18181b', 
            padding: '20px', 
            borderRadius: '8px',
            border: '1px solid #ef4444'
          }}>
            <h2 style={{ color: '#f97316', marginBottom: '10px' }}>Error:</h2>
            <pre style={{ color: '#fbbf24', whiteSpace: 'pre-wrap' }}>
              {this.state.error && this.state.error.toString()}
            </pre>
            <h2 style={{ color: '#f97316', marginTop: '20px', marginBottom: '10px' }}>
              Stack Trace:
            </h2>
            <pre style={{ color: '#a1a1aa', whiteSpace: 'pre-wrap', fontSize: '12px' }}>
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </pre>
          </div>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            Reload Page
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
