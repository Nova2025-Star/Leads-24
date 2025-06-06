import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const CreateQuote = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const leadId = queryParams.get('leadId');

  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quoteItems, setQuoteItems] = useState([
    { id: 1, quantity: 1, tree_species: 'PINE', operation_type: 'FELLING', custom_operation: '', cost: 0 }
  ]);
  const [totalAmount, setTotalAmount] = useState(0);
  const [commissionAmount, setCommissionAmount] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  // Tree species options from backend enum
  const treeSpeciesOptions = [
    { value: 'PINE', label: 'Tall (Pine)' },
    { value: 'SPRUCE', label: 'Gran (Spruce)' },
    { value: 'OAK', label: 'Ek (Oak)' },
    { value: 'BEECH', label: 'Bok (Beech)' },
    { value: 'MAPLE', label: 'Lönn (Maple)' },
    { value: 'ASH', label: 'Ask (Ash)' },
    { value: 'ALDER', label: 'Al (Alder)' },
    { value: 'BIRCH', label: 'Björk (Birch)' },
    { value: 'LINDEN', label: 'Lind (Linden)' },
    { value: 'BIRD_CHERRY', label: 'Hägg (Bird Cherry)' },
    { value: 'ROWAN', label: 'Rönn (Rowan)' },
    { value: 'CHERRY', label: 'Körsbär (Cherry)' },
    { value: 'WALNUT', label: 'Valnöt (Walnut)' },
    { value: 'POPLAR', label: 'Poppel (Poplar)' },
    { value: 'PLANE', label: 'Platan (Plane)' },
    { value: 'WILLOW', label: 'Pil (Willow)' }
  ];

  // Operation types from backend enum
  const operationTypeOptions = [
    { value: 'DEAD_WOOD', label: 'Död veds beskärning' },
    { value: 'FELLING', label: 'Trädfällning' },
    { value: 'SECTION_FELLING', label: 'Sektionsfällning' },
    { value: 'ADVANCED_SECTION_FELLING', label: 'Avancerad sektionsfällning' },
    { value: 'CROWN_REDUCTION', label: 'Kronreducering' },
    { value: 'MAINTENANCE_PRUNING', label: 'Underhållsbeskäring' },
    { value: 'SPACE_PRUNING', label: 'Utrymmesbeskärning' },
    { value: 'CROWN_LIFTING', label: 'Kronlyft' },
    { value: 'POLLARDING', label: 'Hamling' },
    { value: 'OTHER', label: 'Annat' },
    { value: 'REMOVAL', label: 'Bortförsling' },
    { value: 'THINNING', label: 'Urglesing' },
    { value: 'STUMP_GRINDING', label: 'Stubbfräsning' },
    { value: 'CROWN_STABILIZATION', label: 'Kronstabilisering' },
    { value: 'EMERGENCY', label: 'Jour' }
  ];

  useEffect(() => {
    const fetchLead = async () => {
      if (!leadId || !user) return;

      try {
        setLoading(true);
        const response = await axios.get(`/api/v1/partner/leads/${leadId}?partner_id=${user.id}`);
        setLead(response.data);
      } catch (err) {
        setError('Failed to load lead details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchLead();
  }, [leadId, user]);

  useEffect(() => {
    // Calculate total and commission whenever quote items change
    const total = quoteItems.reduce((sum, item) => sum + (parseFloat(item.cost) || 0), 0);
    setTotalAmount(total);
    setCommissionAmount(total * 0.1); // 10% commission
  }, [quoteItems]);

  const handleItemChange = (id, field, value) => {
    const updatedItems = quoteItems.map(item => {
      if (item.id === id) {
        return { ...item, [field]: value };
      }
      return item;
    });
    setQuoteItems(updatedItems);
  };

  const addQuoteItem = () => {
    const newId = Math.max(...quoteItems.map(item => item.id), 0) + 1;
    setQuoteItems([
      ...quoteItems,
      { id: newId, quantity: 1, tree_species: 'PINE', operation_type: 'FELLING', custom_operation: '', cost: 0 }
    ]);
  };

  const removeQuoteItem = (id) => {
    if (quoteItems.length === 1) {
      return; // Don't remove the last item
    }
    setQuoteItems(quoteItems.filter(item => item.id !== id));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!lead) return;
    
    try {
      setSubmitting(true);
      
      // Format quote items for API
      const formattedItems = quoteItems.map(item => ({
        quantity: parseInt(item.quantity),
        tree_species: item.tree_species,
        operation_type: item.operation_type,
        custom_operation: item.operation_type === 'OTHER' ? item.custom_operation : undefined,
        cost: parseFloat(item.cost)
      }));
      
      // Create quote
      const response = await axios.post(`/api/v1/partner/leads/${lead.id}/quote?partner_id=${user.id}`, {
        lead_id: lead.id,
        total_amount: totalAmount,
        commission_amount: commissionAmount,
        items: formattedItems
      });
      
      // Navigate to the quote detail page
      navigate(`/partner/quotes/${response.data.id}`);
    } catch (err) {
      setError('Failed to create quote');
      console.error(err);
    } finally {
      setSubmitting(false);
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

  if (!lead) {
    return (
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
        No lead selected. Please select a lead to create a quote.
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Create Quote</h1>
      
      <div className="mt-4 bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Lead Information</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">{lead.summary}</p>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
          <dl className="sm:divide-y sm:divide-gray-200">
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Customer</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {lead.customer_name}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Address</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {lead.address}, {lead.city}, {lead.postal_code}
              </dd>
            </div>
            <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
              <dt className="text-sm font-medium text-gray-500">Region</dt>
              <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                {lead.region}
              </dd>
            </div>
          </dl>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="mt-8">
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Quote Items</h3>
            <button
              type="button"
              onClick={addQuoteItem}
              className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Add Item
            </button>
          </div>
          
          <div className="border-t border-gray-200">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quantity
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tree Species
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Operation
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost (SEK)
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {quoteItems.map((item) => (
                  <tr key={item.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="number"
                        min="1"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(item.id, 'quantity', e.target.value)}
                        className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-20 sm:text-sm border-gray-300 rounded-md"
                        required
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select
                        value={item.tree_species}
                        onChange={(e) => handleItemChange(item.id, 'tree_species', e.target.value)}
                        className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        required
                      >
                        {treeSpeciesOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <select
                          value={item.operation_type}
                          onChange={(e) => handleItemChange(item.id, 'operation_type', e.target.value)}
                          className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                          required
                        >
                          {operationTypeOptions.map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                        
                        {item.operation_type === 'OTHER' && (
                          <input
                            type="text"
                            value={item.custom_operation}
                            onChange={(e) => handleItemChange(item.id, 'custom_operation', e.target.value)}
                            placeholder="Specify operation"
                            className="mt-2 shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            required
                          />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={item.cost}
                        onChange={(e) => handleItemChange(item.id, 'cost', e.target.value)}
                        className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-32 sm:text-sm border-gray-300 rounded-md"
                        required
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        type="button"
                        onClick={() => removeQuoteItem(item.id)}
                        className="text-red-600 hover:text-red-900"
                        disabled={quoteItems.length === 1}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50">
                <tr>
                  <td colSpan="3" className="px-6 py-4 text-right font-medium">
                    Total:
                  </td>
                  <td className="px-6 py-4 font-medium">
                    {totalAmount.toFixed(2)} SEK
                  </td>
                  <td></td>
                </tr>
                <tr>
                  <td colSpan="3" className="px-6 py-4 text-right font-medium text-gray-500">
                    Commission (10%):
                  </td>
                  <td className="px-6 py-4 font-medium text-gray-500">
                    {commissionAmount.toFixed(2)} SEK
                  </td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={() => navigate('/partner/leads')}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 mr-3"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
              submitting ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
          >
            {submitting ? 'Creating...' : 'Create Quote'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateQuote;
