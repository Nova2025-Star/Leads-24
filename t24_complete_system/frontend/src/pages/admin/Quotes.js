import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Quotes = () => {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuotes = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await axios.get('/api/v1/admin/quotes');
        console.log("Quotes data received:", response.data);
        setQuotes(response.data || []);
      } catch (err) {
        console.error("Error fetching quotes:", err);
        setError('Failed to load quotes. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchQuotes();
  }, []);

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

  // If no quotes are available, show a message
  if (quotes.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-green-700 mb-2">Quotes Overview</h1>
          <p className="text-sm text-gray-500">No quotes available at this time.</p>
        </header>
        
        <div className="bg-white rounded shadow p-6">
          <p className="text-gray-600">There are no quotes in the system yet. Quotes will appear here once partners create them for leads.</p>
          <button className="mt-4 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">
            Go to Leads
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-green-700 mb-2">Quotes Overview</h1>
        <p className="text-sm text-gray-500">Manage and track all quotes in the system.</p>
      </header>

      <div className="bg-white rounded shadow overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-xl font-semibold text-green-700">All Quotes</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quote ID</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lead</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Partner</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {quotes.map((quote) => (
                <tr key={quote.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#{quote.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {quote.lead_name || `Lead #${quote.lead_id}`}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {quote.partner_name || `Partner #${quote.partner_id}`}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {quote.amount?.toLocaleString() || 0} SEK
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${quote.status === 'approved' ? 'bg-green-100 text-green-800' : 
                        quote.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 
                        quote.status === 'declined' ? 'bg-red-100 text-red-800' : 
                        'bg-gray-100 text-gray-800'}`}>
                      {quote.status?.charAt(0).toUpperCase() + quote.status?.slice(1) || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(quote.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-indigo-600 hover:text-indigo-900 mr-3">View</button>
                    <button className="text-green-600 hover:text-green-900 mr-3">Approve</button>
                    <button className="text-red-600 hover:text-red-900">Decline</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Quotes;
