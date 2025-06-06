import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Link } from 'react-router-dom';

const PartnerLeads = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStatus, setSelectedStatus] = useState('');
  const { user } = useAuth();
  const [leadDetails, setLeadDetails] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/v1/partner/leads?partner_id=${user.id}`);
        setLeads(response.data);
      } catch (err) {
        setError('Failed to load leads');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (user && user.id) {
      fetchLeads();
    }
  }, [user]);

  const filteredLeads = leads.filter(lead => {
    if (selectedStatus) {
      return lead.status === selectedStatus;
    }
    return true;
  });

  const statuses = [...new Set(leads.map(lead => lead.status))];

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'assigned':
        return 'bg-yellow-100 text-yellow-800';
      case 'accepted':
        return 'bg-blue-100 text-blue-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'quoted':
        return 'bg-purple-100 text-purple-800';
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'declined':
        return 'bg-orange-100 text-orange-800';
      case 'completed':
        return 'bg-indigo-100 text-indigo-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const viewLeadDetails = async (leadId) => {
    try {
      const response = await axios.get(`/api/v1/partner/leads/${leadId}?partner_id=${user.id}`);
      setLeadDetails(response.data);
      setShowDetailsModal(true);
    } catch (err) {
      setError('Failed to load lead details');
      console.error(err);
    }
  };

  const closeDetailsModal = () => {
    setShowDetailsModal(false);
    setLeadDetails(null);
  };

  const acceptLead = async (leadId) => {
    try {
      await axios.post(`/api/v1/partner/leads/${leadId}/accept?partner_id=${user.id}`);
      
      // Update the lead in the local state
      const updatedLeads = leads.map(lead => {
        if (lead.id === leadId) {
          return {
            ...lead,
            status: 'accepted'
          };
        }
        return lead;
      });
      
      setLeads(updatedLeads);
      
      // If the details modal is open, update the lead details
      if (leadDetails && leadDetails.id === leadId) {
        setLeadDetails({
          ...leadDetails,
          status: 'accepted'
        });
      }
    } catch (err) {
      setError('Failed to accept lead');
      console.error(err);
    }
  };

  const rejectLead = async (leadId) => {
    try {
      await axios.post(`/api/v1/partner/leads/${leadId}/reject?partner_id=${user.id}`);
      
      // Update the lead in the local state
      const updatedLeads = leads.map(lead => {
        if (lead.id === leadId) {
          return {
            ...lead,
            status: 'rejected'
          };
        }
        return lead;
      });
      
      setLeads(updatedLeads);
      closeDetailsModal();
    } catch (err) {
      setError('Failed to reject lead');
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
      <h1 className="text-2xl font-semibold text-gray-900">Your Leads</h1>

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

      {/* Leads Table */}
      <div className="mt-8 flex flex-col">
        <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
            <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Region
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Summary
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
                  {filteredLeads.length > 0 ? (
                    filteredLeads.map((lead) => (
                      <tr key={lead.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{lead.region}</div>
                          <div className="text-sm text-gray-500">{lead.city}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900 truncate max-w-xs">{lead.summary}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(lead.status)}`}>
                            {lead.status.charAt(0).toUpperCase() + lead.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(lead.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => viewLeadDetails(lead.id)}
                              className="text-indigo-600 hover:text-indigo-900"
                            >
                              View
                            </button>
                            
                            {lead.status === 'assigned' && (
                              <>
                                <button
                                  onClick={() => acceptLead(lead.id)}
                                  className="text-green-600 hover:text-green-900"
                                >
                                  Accept
                                </button>
                                <button
                                  onClick={() => rejectLead(lead.id)}
                                  className="text-red-600 hover:text-red-900"
                                >
                                  Reject
                                </button>
                              </>
                            )}
                            
                            {lead.status === 'accepted' && (
                              <Link
                                to={`/partner/quotes/new?leadId=${lead.id}`}
                                className="text-blue-600 hover:text-blue-900"
                              >
                                Create Quote
                              </Link>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">
                        No leads found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Lead Details Modal */}
      {showDetailsModal && leadDetails && (
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
                      Lead Details
                    </h3>
                    <div className="mt-4 space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-gray-500">Summary</h4>
                        <p className="mt-1 text-sm text-gray-900">{leadDetails.summary}</p>
                      </div>
                      
                      {leadDetails.status === 'accepted' || leadDetails.status === 'quoted' || leadDetails.status === 'approved' ? (
                        <>
                          <div>
                            <h4 className="text-sm font-medium text-gray-500">Customer</h4>
                            <p className="mt-1 text-sm text-gray-900">{leadDetails.customer_name}</p>
                            <p className="text-sm text-gray-900">{leadDetails.customer_email}</p>
                            <p className="text-sm text-gray-900">{leadDetails.customer_phone}</p>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-medium text-gray-500">Address</h4>
                            <p className="mt-1 text-sm text-gray-900">{leadDetails.address}</p>
                            <p className="text-sm text-gray-900">{leadDetails.city}, {leadDetails.postal_code}</p>
                            <p className="text-sm text-gray-900">{leadDetails.region}</p>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-medium text-gray-500">Details</h4>
                            <p className="mt-1 text-sm text-gray-900">{leadDetails.details}</p>
                          </div>
                        </>
                      ) : (
                        <div className="bg-yellow-50 p-4 rounded-md">
                          <div className="flex">
                            <div className="flex-shrink-0">
                              <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                              </svg>
                            </div>
                            <div className="ml-3">
                              <h3 className="text-sm font-medium text-yellow-800">Accept the lead to view full details</h3>
                              <div className="mt-2 text-sm text-yellow-700">
                                <p>
                                  You must accept this lead to view customer contact information and full details. 
                                  Once accepted, you will be charged 500 SEK for this lead.
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-500">Status</h4>
                        <p className="mt-1">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(leadDetails.status)}`}>
                            {leadDetails.status.charAt(0).toUpperCase() + leadDetails.status.slice(1)}
                          </span>
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                {leadDetails.status === 'assigned' && (
                  <>
                    <button
                      type="button"
                      className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm"
                      onClick={() => acceptLead(leadDetails.id)}
                    >
                      Accept Lead
                    </button>
                    <button
                      type="button"
                      className="mt-3 w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                      onClick={() => rejectLead(leadDetails.id)}
                    >
                      Reject Lead
                    </button>
                  </>
                )}
                
                {leadDetails.status === 'accepted' && (
                  <Link
                    to={`/partner/quotes/new?leadId=${leadDetails.id}`}
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                  >
                    Create Quote
                  </Link>
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

export default PartnerLeads;
