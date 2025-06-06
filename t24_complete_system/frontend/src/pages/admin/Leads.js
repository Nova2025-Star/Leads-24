import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

const AdminLeads = () => {
  const [leads, setLeads] = useState([]);
  const [partners, setPartners] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRegion, setSelectedRegion] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState(null);
  const [selectedPartner, setSelectedPartner] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch leads
        const leadsResponse = await axios.get('/api/v1/admin/leads');
        setLeads(leadsResponse.data);
        
        // Fetch partners
        const partnersResponse = await axios.get('/api/v1/admin/partners');
        setPartners(partnersResponse.data);
      } catch (err) {
        setError('Failed to load data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredLeads = leads.filter(lead => {
    let matchesRegion = true;
    let matchesStatus = true;
    
    if (selectedRegion) {
      matchesRegion = lead.region === selectedRegion;
    }
    
    if (selectedStatus) {
      matchesStatus = lead.status === selectedStatus;
    }
    
    return matchesRegion && matchesStatus;
  });

  const regions = [...new Set(leads.map(lead => lead.region))];
  const statuses = [...new Set(leads.map(lead => lead.status))];

  const openAssignModal = (lead) => {
    setSelectedLead(lead);
    setSelectedPartner('');
    setAssignModalOpen(true);
  };

  const closeAssignModal = () => {
    setAssignModalOpen(false);
    setSelectedLead(null);
  };

  const handleAssign = async () => {
    if (!selectedLead || !selectedPartner) return;
    
    try {
      await axios.post(`/api/v1/admin/leads/${selectedLead.id}/assign/${selectedPartner}`);
      
      // Update the lead in the local state
      const updatedLeads = leads.map(lead => {
        if (lead.id === selectedLead.id) {
          return {
            ...lead,
            assigned_partner_id: parseInt(selectedPartner),
            status: 'assigned'
          };
        }
        return lead;
      });
      
      setLeads(updatedLeads);
      closeAssignModal();
    } catch (err) {
      setError('Failed to assign lead');
      console.error(err);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'new':
        return 'bg-gray-100 text-gray-800';
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
      case 'expired':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
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
    <div>
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold text-gray-900">Manage Leads</h1>
        <Link
          to="/admin/leads/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          Add New Lead
        </Link>
      </div>

      {/* Filters */}
      <div className="mt-4 flex flex-wrap gap-4">
        <div>
          <label htmlFor="region" className="block text-sm font-medium text-gray-700">
            Filter by Region
          </label>
          <select
            id="region"
            name="region"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
          >
            <option value="">All Regions</option>
            {regions.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700">
            Filter by Status
          </label>
          <select
            id="status"
            name="status"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
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
                      Customer
                    </th>
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
                  {filteredLeads.map((lead) => (
                    <tr key={lead.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{lead.customer_name}</div>
                        <div className="text-sm text-gray-500">{lead.customer_email}</div>
                      </td>
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
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex space-x-2">
                          <Link to={`/admin/leads/${lead.id}`} className="text-indigo-600 hover:text-indigo-900">
                            View
                          </Link>
                          {lead.status === 'new' && (
                            <button
                              onClick={() => openAssignModal(lead)}
                              className="text-green-600 hover:text-green-900"
                            >
                              Assign
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Assign Modal */}
      {assignModalOpen && (
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
                      Assign Lead to Partner
                    </h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500 mb-4">
                        Select a partner to assign this lead to:
                      </p>
                      <div className="mb-4">
                        <p className="font-medium text-gray-700">{selectedLead?.summary}</p>
                        <p className="text-sm text-gray-500">{selectedLead?.region}</p>
                      </div>
                      <select
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
                        value={selectedPartner}
                        onChange={(e) => setSelectedPartner(e.target.value)}
                      >
                        <option value="">Select a Partner</option>
                        {partners
                          .filter(partner => partner.region === selectedLead?.region || !partner.region)
                          .map((partner) => (
                            <option key={partner.id} value={partner.id}>
                              {partner.full_name} {partner.region ? `(${partner.region})` : ''}
                            </option>
                          ))}
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={handleAssign}
                  disabled={!selectedPartner}
                >
                  Assign
                </button>
                <button
                  type="button"
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={closeAssignModal}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminLeads;
