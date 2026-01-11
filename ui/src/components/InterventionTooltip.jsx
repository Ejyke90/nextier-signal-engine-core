import { X, AlertTriangle, TrendingUp, Users, Droplet, DollarSign } from 'lucide-react'

const INTERVENTION_STRATEGIES = {
  Economic: {
    icon: DollarSign,
    color: '#f59e0b',
    actions: [
      'Deploy emergency food aid and subsidies',
      'Establish temporary employment programs',
      'Provide microfinance support for small businesses',
      'Negotiate fuel price stabilization measures'
    ]
  },
  Environmental: {
    icon: Droplet,
    color: '#10b981',
    actions: [
      'Deploy food aid and water resources',
      'Establish grazing reserves and migration corridors',
      'Implement climate adaptation programs',
      'Provide agricultural support and drought-resistant seeds'
    ]
  },
  Social: {
    icon: Users,
    color: '#ef4444',
    actions: [
      'Increase community policing presence',
      'Deploy peace-building and dialogue initiatives',
      'Monitor and counter hate speech on social media',
      'Engage religious and community leaders for de-escalation'
    ]
  }
}

const InterventionTooltip = ({ signal, onClose, position }) => {
  if (!signal) return null

  const driver = signal.conflict_driver || 'Social'
  const strategy = INTERVENTION_STRATEGIES[driver] || INTERVENTION_STRATEGIES.Social
  const Icon = strategy.icon

  return (
    <>
      <div className="intervention-overlay" onClick={onClose} />
      <div 
        className="intervention-tooltip"
        style={{
          left: position?.x ? `${position.x}px` : '50%',
          top: position?.y ? `${position.y}px` : '50%',
          transform: position?.x ? 'translate(-50%, -100%)' : 'translate(-50%, -50%)'
        }}
      >
        <div className="tooltip-header">
          <div className="header-content">
            <AlertTriangle size={20} className="warning-icon" />
            <div>
              <h3 className="tooltip-title">Critical Risk Zone</h3>
              <p className="tooltip-location">{signal.state} / {signal.lga}</p>
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="tooltip-body">
          <div className="risk-metrics">
            <div className="metric">
              <span className="metric-label">Risk Score</span>
              <span className="metric-value risk-score">{signal.risk_score}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Event Type</span>
              <span className="metric-value">{signal.event_type}</span>
            </div>
            <div className="metric">
              <span className="metric-label">Severity</span>
              <span className="metric-value severity">{signal.severity}</span>
            </div>
          </div>

          <div className="driver-section">
            <div className="driver-header" style={{ color: strategy.color }}>
              <Icon size={18} />
              <span>Primary Driver: {driver}</span>
            </div>
            {signal.sentiment_intensity && (
              <div className="sentiment-bar">
                <span className="sentiment-label">Sentiment Intensity</span>
                <div className="sentiment-track">
                  <div 
                    className="sentiment-fill"
                    style={{ 
                      width: `${signal.sentiment_intensity}%`,
                      backgroundColor: signal.sentiment_intensity > 70 ? '#ef4444' : '#f59e0b'
                    }}
                  />
                </div>
                <span className="sentiment-value">{signal.sentiment_intensity}%</span>
              </div>
            )}
          </div>

          <div className="intervention-section">
            <h4 className="intervention-title">
              <TrendingUp size={16} />
              Suggested Interventions
            </h4>
            <ul className="intervention-list">
              {strategy.actions.map((action, index) => (
                <li key={index} className="intervention-item">
                  <span className="bullet" style={{ backgroundColor: strategy.color }} />
                  {action}
                </li>
              ))}
            </ul>
          </div>

          {signal.hate_speech_indicators && signal.hate_speech_indicators.length > 0 && (
            <div className="alert-section">
              <div className="alert-header">
                <AlertTriangle size={14} />
                <span>Hate Speech Detected</span>
              </div>
              <div className="hate-speech-tags">
                {signal.hate_speech_indicators.map((indicator, index) => (
                  <span key={index} className="hate-speech-tag">{indicator}</span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="tooltip-footer">
          <button className="action-btn primary">Deploy Response Team</button>
          <button className="action-btn secondary">View Full Report</button>
        </div>
      </div>

      <style jsx>{`
        .intervention-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 9998;
          backdrop-filter: blur(2px);
        }

        .intervention-tooltip {
          position: fixed;
          width: 450px;
          max-width: 90vw;
          background: #1f2937;
          border: 1px solid #374151;
          border-radius: 12px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
          z-index: 9999;
          animation: slideIn 0.2s ease-out;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translate(-50%, -90%);
          }
          to {
            opacity: 1;
            transform: translate(-50%, -100%);
          }
        }

        .tooltip-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 20px;
          border-bottom: 1px solid #374151;
        }

        .header-content {
          display: flex;
          gap: 12px;
          align-items: flex-start;
        }

        .warning-icon {
          color: #ef4444;
          flex-shrink: 0;
          margin-top: 2px;
        }

        .tooltip-title {
          font-size: 16px;
          font-weight: 600;
          color: #f3f4f6;
          margin: 0 0 4px 0;
        }

        .tooltip-location {
          font-size: 13px;
          color: #9ca3af;
          margin: 0;
        }

        .close-btn {
          background: transparent;
          border: none;
          color: #9ca3af;
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          transition: all 0.2s;
        }

        .close-btn:hover {
          background: #374151;
          color: #f3f4f6;
        }

        .tooltip-body {
          padding: 20px;
          max-height: 60vh;
          overflow-y: auto;
        }

        .risk-metrics {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 12px;
          margin-bottom: 20px;
        }

        .metric {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .metric-label {
          font-size: 11px;
          color: #9ca3af;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .metric-value {
          font-size: 16px;
          font-weight: 600;
          color: #f3f4f6;
        }

        .metric-value.risk-score {
          color: #ef4444;
        }

        .metric-value.severity {
          text-transform: capitalize;
        }

        .driver-section {
          background: #111827;
          border-radius: 8px;
          padding: 15px;
          margin-bottom: 20px;
        }

        .driver-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 12px;
        }

        .sentiment-bar {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .sentiment-label {
          font-size: 12px;
          color: #9ca3af;
          min-width: 120px;
        }

        .sentiment-track {
          flex: 1;
          height: 8px;
          background: #374151;
          border-radius: 4px;
          overflow: hidden;
        }

        .sentiment-fill {
          height: 100%;
          transition: width 0.3s ease;
        }

        .sentiment-value {
          font-size: 12px;
          font-weight: 600;
          color: #f3f4f6;
          min-width: 40px;
          text-align: right;
        }

        .intervention-section {
          margin-bottom: 20px;
        }

        .intervention-title {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          font-weight: 600;
          color: #f3f4f6;
          margin: 0 0 12px 0;
        }

        .intervention-list {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .intervention-item {
          display: flex;
          align-items: flex-start;
          gap: 10px;
          font-size: 13px;
          color: #d1d5db;
          line-height: 1.5;
        }

        .bullet {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          flex-shrink: 0;
          margin-top: 7px;
        }

        .alert-section {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 8px;
          padding: 12px;
        }

        .alert-header {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          font-weight: 600;
          color: #ef4444;
          margin-bottom: 8px;
        }

        .hate-speech-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .hate-speech-tag {
          background: rgba(239, 68, 68, 0.2);
          color: #fca5a5;
          font-size: 11px;
          padding: 4px 8px;
          border-radius: 4px;
          border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .tooltip-footer {
          display: flex;
          gap: 10px;
          padding: 15px 20px;
          border-top: 1px solid #374151;
        }

        .action-btn {
          flex: 1;
          padding: 10px 16px;
          border-radius: 8px;
          font-size: 13px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
        }

        .action-btn.primary {
          background: #3b82f6;
          color: white;
        }

        .action-btn.primary:hover {
          background: #2563eb;
        }

        .action-btn.secondary {
          background: #374151;
          color: #d1d5db;
        }

        .action-btn.secondary:hover {
          background: #4b5563;
        }
      `}</style>
    </>
  )
}

export default InterventionTooltip
