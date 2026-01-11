import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div style={{ padding: '20px', background: '#09090b', minHeight: '100vh', color: 'white' }}>
      <h1 style={{ color: 'white', fontSize: '48px' }}>SIMPLE TEST APP</h1>
      <p style={{ color: 'white', fontSize: '24px' }}>If you can see this, React is working!</p>
      <button 
        onClick={() => setCount(count + 1)}
        style={{ 
          padding: '10px 20px', 
          fontSize: '18px', 
          background: 'red', 
          color: 'white',
          border: 'none',
          cursor: 'pointer'
        }}
      >
        Count: {count}
      </button>
    </div>
  )
}

export default App
