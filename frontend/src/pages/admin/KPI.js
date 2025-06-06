import React, { useState, useEffect } from 'react';
import axios from 'axios';

const KPI = () => {
  const [kpiData, setKpiData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('week');

  useEffect(() => {
    const fetchKPIData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/v1/admin/kpi?time_range=${timeRange}`);
        setKpiData(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching KPI data:', err);
        setError('Failed to load KPI data');
      } finally {
        setLoading(false);
      }
    };

    fetchKPIData();
  }, [timeRange]);

  const handleTimeRangeChange = (e) => {
    setTimeRange(e.target.value);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">KPI Dashboard</h1>
        <div className="flex items-center">
          <label htmlFor="time-range" className="mr-2 text-sm font-medium text-gray-700">Time Range:</label>
          <select
            id="time-range"
            value={timeRange}
            onChange={handleTimeRangeChange}
            className="mt-1 block pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md shadow-sm"
          >
            <option value="day">Last 24 Hours</option>
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="year">Last Year</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      {kpiData && kpiData.metrics && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {/* Response Time */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Partner Response Time</div>
            <div className="mt-1 text-3xl font-semibold text-green-600">
              {kpiData.metrics.avg_partner_response_time ? 
                `${Math.round(kpiData.metrics.avg_partner_response_time)} h` : 
                'N/A'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Average time to accept/reject leads</div>
          </div>

          {/* Quote Creation Time */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Quote Creation Time</div>
            <div className="mt-1 text-3xl font-semibold text-blue-600">
              {kpiData.metrics.avg_quote_submission_time ? 
                `${Math.round(kpiData.metrics.avg_quote_submission_time)} h` : 
                'N/A'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Average time to create quotes</div>
          </div>

          {/* Customer Decision Time */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Customer Decision Time</div>
            <div className="mt-1 text-3xl font-semibold text-purple-600">
              {kpiData.metrics.avg_customer_decision_time ? 
                `${Math.round(kpiData.metrics.avg_customer_decision_time)} h` : 
                'N/A'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Average time for customer decisions</div>
          </div>

          {/* Quotes Accepted */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Quotes Accepted</div>
            <div className="mt-1 text-3xl font-semibold text-green-600">
              {kpiData.metrics.quotes_accepted_percent ? 
                `${Math.round(kpiData.metrics.quotes_accepted_percent)}%` : 
                '0%'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Percentage of quotes accepted</div>
          </div>

          {/* Missed Leads */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Missed Leads</div>
            <div className="mt-1 text-3xl font-semibold text-red-600">
              {kpiData.metrics.missed_leads_count || '0'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Number of expired or rejected leads</div>
          </div>

          {/* Average Job Value */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Average Job Value</div>
            <div className="mt-1 text-3xl font-semibold text-blue-600">
              {kpiData.metrics.average_job_value ? 
                `${Math.round(kpiData.metrics.average_job_value).toLocaleString()} SEK` : 
                '0 SEK'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Average value of accepted quotes</div>
          </div>

          {/* Lead Assignment Time */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Lead Assignment Time</div>
            <div className="mt-1 text-3xl font-semibold text-yellow-600">
              {kpiData.metrics.avg_lead_assignment_time ? 
                `${Math.round(kpiData.metrics.avg_lead_assignment_time)} h` : 
                'N/A'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Average time to assign leads</div>
          </div>

          {/* Total Revenue */}
          <div className="bg-white overflow-hidden shadow rounded-lg p-5">
            <div className="text-sm font-medium text-gray-500 truncate">Total Revenue</div>
            <div className="mt-1 text-3xl font-semibold text-green-600">
              {kpiData.metrics.total_revenue ? 
                `${Math.round(kpiData.metrics.total_revenue).toLocaleString()} SEK` : 
                '0 SEK'}
            </div>
            <div className="mt-1 text-sm text-gray-500">Total revenue in period</div>
          </div>
        </div>
      )}

      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent KPI Events</h2>
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-700">System Activity</h3>
          </div>
          <div className="px-4 py-5 sm:p-6">
            {kpiData && kpiData.events && kpiData.events.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Event Type
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Lead ID
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User ID
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Data
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Time
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {kpiData.events.map((event) => (
                      <tr key={event.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            event.event_type.includes("created") ? "bg-green-100 text-green-800" :
                            event.event_type.includes("accepted") ? "bg-blue-100 text-blue-800" :
                            event.event_type.includes("rejected") ? "bg-red-100 text-red-800" :
                            event.event_type.includes("expired") ? "bg-yellow-100 text-yellow-800" :
                            "bg-gray-100 text-gray-800"
                          }`}>
                            {event.event_type}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {event.lead_id || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {event.user_id || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {event.data || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(event.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">No events found for the selected time range.</p>
            )}
          </div>
          <div className="bg-gray-50 px-4 py-4 sm:px-6">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                Showing {kpiData?.events?.length || 0} of {kpiData?.events_count || 0} events
              </div>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200">View All Events</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KPI;
