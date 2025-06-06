import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Link } from 'react-router-dom';

const PartnerQuotes = () => {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStatus, setSelectedStatus] = useState('');
  const { user } = useAuth();
  const [quoteDetails, setQuoteDetails] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    const fetchQuotes = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/v1/partner/quotes?partner_id=${user.id}`);
        setQuotes(response.data);
      } catch (err) {
        setError('Failed to load quotes');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (user && user.id) {
      fetchQuotes();
    }
  }, [user]);

  const filteredQuotes = quotes.filter(quote => {
    if (selectedStatus) {
      return quote.status === selectedStatus;
    }
    return true;
  });

  const statuses = [...new Set(quotes.map(quote => quote.status))];

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'sent':
        return 'bg-blue-100 text-blue-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'declined':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const viewQuoteDetails = async (quoteId) => {
    try {
      const response = await axios.get(`/api/v1/quotes/${quoteId}`);
      setQuoteDetails(response.data);
      setShowDetailsModal(true);
    } catch (err) {
      setError('Failed to load quote details');
      console.error(err);
    }
  };

  const closeDetailsModal = () => {
    setShowDetailsModal(false);
    setQuoteDetails(null);
  };

  const sendQuoteToCustomer = async (quoteId) => {
    try {
      await axios.post(`/api/v1/partner/quotes/${quoteId}/send?partner_id=${user.id}`);
      
      // Update the quote in the local state
      const updatedQuotes = quotes.map(quote => {
        if (quote.id === quoteId) {
          return {
            ...quote,
            status: 'sent'
          };
        }
        return quote;
      });
      
      setQuotes(updatedQuotes);
      
      // If the details modal is open, update the quote details
      if (quoteDetails && quoteDetails.id === quoteId) {
        setQuoteDetails({
          ...quoteDetails,
          status: 'sent'
        });
      }
    } catch (err) {
      setError('Failed to send quote');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
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
    <div>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Your Quotes</h1>
        <Link
          to="/partner/leads"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          View Leads
        </Link>
      </div>

      {/* Filters */}
      <div className="mt-4">
        <label htmlFor="status" className="block text-sm font-medium text-gray-700">
          Filter by Status
        </label>
        <select
          id="status"
          name="status"
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
        >
          <option value="">All Statuses</option>
          {statuses.map((status) => (
            <option key={status} value={status}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </option>
          ))}
        </select>
      </div>

      {/* Quotes Table */}
      <div className="mt-8 flex flex-col">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quote ID
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Lead ID
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredQuotes.length > 0 ? (
                    filteredQuotes.map((quote) => (
                      <tr key={quote.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">#{quote.id}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">#{quote.lead_id}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{quote.total_amount.toLocaleString()} SEK</div>
                          <div className="text-xs text-gray-500">Commission: {quote.commission_amount.toLocaleString()} SEK</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(quote.status)}`}>
                            {quote.status.charAt(0).toUpperCase() + quote.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(quote.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => viewQuoteDetails(quote.id)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              View
                            </button>
                            
                            {quote.status === 'draft' && (
                              <button
                                onClick={() => sendQuoteToCustomer(quote.id)}
                                className="text-green-600 hover:text-green-900"
                              >
                                Send to Customer
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                        No quotes found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Quote Details Modal */}
      {showDetailsModal && quoteDetails && (
        <div className="fixed z-10 inset-0 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>

            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                    <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                      Quote Details
                    </h3>
                    <div className="mt-4">
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium text-gray-500">Quote ID:</span>
                        <span className="text-sm text-gray-900">#{quoteDetails.id}</span>
                      </div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium text-gray-500">Lead ID:</span>
                        <span className="text-sm text-gray-900">#{quoteDetails.lead_id}</span>
                      </div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium text-gray-500">Status:</span>
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(quoteDetails.status)}`}>
                          {quoteDetails.status.charAt(0).toUpperCase() + quoteDetails.status.slice(1)}
                        </span>
                      </div>
                      <div className="flex justify-between mb-2">
                        <span className="text-sm font-medium text-gray-500">Created:</span>
                        <span className="text-sm text-gray-900">{new Date(quoteDetails.created_at).toLocaleString()}</span>
                      </div>
                      {quoteDetails.sent_at && (
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium text-gray-500">Sent:</span>
                          <span className="text-sm text-gray-900">{new Date(quoteDetails.sent_at).toLocaleString()}</span>
                        </div>
                      )}
                      {quoteDetails.customer_response_at && (
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium text-gray-500">Customer Response:</span>
                          <span className="text-sm text-gray-900">{new Date(quoteDetails.customer_response_at).toLocaleString()}</span>
                        </div>
                      )}
                      
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Quote Items</h4>
                        <div className="border rounded-md overflow-hidden">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Qty
                                </th>
                                <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Tree
                                </th>
                                <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Operation
                                </th>
                                <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Cost
                                </th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {quoteDetails.items && quoteDetails.items.map((item) => (
                                <tr key={item.id}>
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                                    {item.quantity}
                                  </td>
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                                    {item.tree_species}
                                  </td>
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                                    {item.operation_type}
                                    {item.custom_operation && ` (${item.custom_operation})`}
                                  </td>
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                                    {item.cost.toLocaleString()} SEK
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                            <tfoot className="bg-gray-50">
                              <tr>
                                <td colSpan="3" className="px-3 py-2 text-right text-xs font-medium">
                                  Total:
                                </td>
                                <td className="px-3 py-2 text-xs font-medium">
                                  {quoteDetails.total_amount.toLocaleString()} SEK
                                </td>
                              </tr>
                              <tr>
                                <td colSpan="3" className="px-3 py-2 text-right text-xs font-medium text-gray-500">
                                  Commission (10%):
                                </td>
                                <td className="px-3 py-2 text-xs font-medium text-gray-500">
                                  {quoteDetails.commission_amount.toLocaleString()} SEK
                                </td>
                              </tr>
                            </tfoot>
                          </table>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                {quoteDetails.status === 'draft' && (
                  <button
                    type="button"
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm"
                    onClick={() => sendQuoteToCustomer(quoteDetails.id)}
                  >
                    Send to Customer
                  </button>
                )}
                
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={closeDetailsModal}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PartnerQuotes;
