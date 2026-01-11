import { MapPin, AlertTriangle, Activity, Shield } from 'lucide-react'

const LiveSignalTicker = ({ signals, onLocationClick, loading }) => {
  const getRiskColor = (score) => {
    if (score >= 80) return 'border-red-500 bg-red-900/10'
    if (score >= 60) return 'border-orange-500 bg-orange-900/10'
    if (score >= 40) return 'border-yellow-500 bg-yellow-900/10'
    return 'border-green-500 bg-green-900/10'
  }

  const getRiskBadgeColor = (score) => {
    if (score >= 80) return 'bg-red-500 text-white'
    if (score >= 60) return 'bg-orange-500 text-white'
    if (score >= 40) return 'bg-yellow-500 text-black'
    return 'bg-green-500 text-white'
  }

  return (
    <div className="col-span-2 bg-bg-secondary border-r border-gray-800 overflow-y-auto">
      <div className="p-6 border-b border-gray-800 sticky top-0 z-10 bg-bg-secondary">
        <h3 className="text-lg font-bold text-white flex items-center">
          <Activity className="w-6 h-6 text-red-500 mr-3 animate-pulse" />
          LIVE SIGNAL TICKER
        </h3>
        <p className="text-xs text-gray-400 mt-2">Real-time threat monitoring</p>
        <div className="mt-3 flex items-center space-x-2">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-red-400 font-semibold">STREAMING</span>
        </div>
      </div>
      
      <div className="p-4 space-y-3">
        {loading ? (
          <div className="text-gray-500 text-sm text-center py-8">Loading signals...</div>
        ) : signals.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-8">No signals detected</div>
        ) : (
          signals.map((signal, index) => (
            <div
              key={index}
              className={`border-l-3 ${getRiskColor(signal.risk_score)} border-l-4 rounded-lg p-4 hover:bg-gray-800/50 transition-all cursor-pointer group`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h4 className="text-white font-semibold text-sm">{signal.lga}, {signal.state}</h4>
                    {signal.veracity_score > 0.8 && (
                      <div 
                        className="flex items-center space-x-1 bg-blue-500/20 border border-blue-500/50 px-2 py-0.5 rounded-full group relative cursor-help"
                        title="Triangulated across multiple credible sources"
                      >
                        <Shield className="w-3 h-3 text-blue-400" />
                        <span className="text-blue-400 text-xs font-semibold">Verified</span>
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 border border-blue-500/30">
                          Triangulated across multiple credible sources
                          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1 border-4 border-transparent border-t-gray-900"></div>
                        </div>
                      </div>
                    )}
                  </div>
                  <p className="text-gray-400 text-xs mt-1 capitalize">{signal.event_type}</p>
                </div>
                <span className={`${getRiskBadgeColor(signal.risk_score)} px-2 py-1 rounded text-xs font-bold`}>
                  {signal.risk_score}
                </span>
              </div>
              
              <div className="flex items-center justify-between mt-3">
                <div className="flex items-center space-x-3 text-xs text-gray-400">
                  <span className="flex items-center">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    {signal.severity}
                  </span>
                  <span>{signal.risk_level}</span>
                </div>
                
                <button
                  onClick={() => onLocationClick(signal)}
                  className="flex items-center space-x-1 text-blue-400 hover:text-blue-300 text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <MapPin className="w-3 h-3" />
                  <span>Locate</span>
                </button>
              </div>
              
              {signal.fuel_price && (
                <div className="mt-2 pt-2 border-t border-gray-700 text-xs text-gray-500">
                  Fuel: ₦{signal.fuel_price}/L | Inflation: {signal.inflation}%
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default LiveSignalTicker
