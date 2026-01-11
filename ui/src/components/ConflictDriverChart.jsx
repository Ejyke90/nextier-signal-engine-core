import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

const DRIVER_COLORS = {
  Economic: '#f59e0b',
  Environmental: '#10b981',
  Social: '#ef4444'
}

const ConflictDriverChart = ({ riskSignals }) => {
  const driverData = useMemo(() => {
    if (!riskSignals || riskSignals.length === 0) {
      return []
    }

    // Count signals by conflict driver
    const driverCounts = {
      Economic: 0,
      Environmental: 0,
      Social: 0,
      Unknown: 0
    }

    riskSignals.forEach(signal => {
      const driver = signal.conflict_driver || 'Unknown'
      if (driverCounts.hasOwnProperty(driver)) {
        driverCounts[driver]++
      } else {
        driverCounts.Unknown++
      }
    })

    // Convert to chart data format
    return Object.entries(driverCounts)
      .filter(([driver, count]) => driver !== 'Unknown' && count > 0)
      .map(([driver, count]) => ({
        driver,
        count,
        percentage: ((count / riskSignals.length) * 100).toFixed(1)
      }))
      .sort((a, b) => b.count - a.count)
  }, [riskSignals])

  if (driverData.length === 0) {
    return (
      <div className="conflict-driver-chart">
        <h3 className="chart-title">Conflict Driver Breakdown</h3>
        <div className="no-data">No conflict driver data available</div>
      </div>
    )
  }

  return (
    <div className="conflict-driver-chart">
      <h3 className="chart-title">Conflict Driver Breakdown</h3>
      <p className="chart-subtitle">Primary causes of current risk signals</p>
      
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={driverData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="driver" 
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1f2937', 
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#f3f4f6'
            }}
            formatter={(value, name, props) => [
              `${value} signals (${props.payload.percentage}%)`,
              'Count'
            ]}
          />
          <Legend 
            wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }}
          />
          <Bar 
            dataKey="count" 
            name="Risk Signals"
            radius={[8, 8, 0, 0]}
          >
            {driverData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={DRIVER_COLORS[entry.driver] || '#6b7280'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="driver-legend">
        {driverData.map(({ driver, count, percentage }) => (
          <div key={driver} className="driver-item">
            <div 
              className="driver-color" 
              style={{ backgroundColor: DRIVER_COLORS[driver] }}
            />
            <span className="driver-name">{driver}</span>
            <span className="driver-count">{count} ({percentage}%)</span>
          </div>
        ))}
      </div>

      <style jsx>{`
        .conflict-driver-chart {
          background: #1f2937;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .chart-title {
          font-size: 18px;
          font-weight: 600;
          color: #f3f4f6;
          margin: 0 0 5px 0;
        }

        .chart-subtitle {
          font-size: 13px;
          color: #9ca3af;
          margin: 0 0 20px 0;
        }

        .no-data {
          text-align: center;
          padding: 40px;
          color: #6b7280;
          font-size: 14px;
        }

        .driver-legend {
          display: flex;
          gap: 20px;
          margin-top: 15px;
          flex-wrap: wrap;
        }

        .driver-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #d1d5db;
        }

        .driver-color {
          width: 12px;
          height: 12px;
          border-radius: 3px;
        }

        .driver-name {
          font-weight: 500;
        }

        .driver-count {
          color: #9ca3af;
        }
      `}</style>
    </div>
  )
}

export default ConflictDriverChart
