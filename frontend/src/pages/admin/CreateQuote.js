import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import '../../enhanced_styles.css';

const CreateQuote = () => {
  const { token } = useAuth();
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState('');
  const [items, setItems] = useState([{
    quantity: 1,
    tree_species: 'PINE',
    operation_type: 'FELLING',
    custom_operation: '',
    cost: 0
  }]);
  const [totalAmount, setTotalAmount] = useState(0);
  const [commissionAmount, setCommissionAmount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchLeads = async () => {
      setLoading(true);
      try {
        const response = await axios.get('/api/v1/admin/leads', {
          headers: { Authorization: `Bearer ${token}` },
          params: { status: 'ACCEPTED' }
        });
        setLeads(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching leads:', err);
        setError('Failed to load leads. Please try again later.');
        setLoading(false);
      }
    };

    fetchLeads();

    // Check if there's a leadId in the URL query params
    const urlParams = new URLSearchParams(window.location.search);
    const leadId = urlParams.get('leadId');
    if (leadId) {
      setSelectedLead(leadId);
    }
  }, [token]);

  // Calculate total amount whenever items change
  useEffect(() => {
    const total = items.reduce((sum, item) => sum + (item.quantity * item.cost), 0);
    setTotalAmount(total);
    setCommissionAmount(total * 0.1); // 10% commission
  }, [items]);

  const handleAddRow = () => {
    setItems([...items, {
      quantity: 1,
      tree_species: 'PINE',
      operation_type: 'FELLING',
      custom_operation: '',
      cost: 0
    }]);
  };

  const handleRemoveRow = (index) => {
    const newItems = [...items];
    newItems.splice(index, 1);
    setItems(newItems);
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...items];
    newItems[index][field] = value;
    setItems(newItems);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedLead) {
      setError('Please select a lead');
      return;
    }

    if (items.length === 0) {
      setError('Please add at least one item');
      return;
    }

    try {
      const response = await axios.post(`/api/v1/partner/leads/${selectedLead}/quote`, {
        total_amount: totalAmount,
        commission_amount: commissionAmount,
        items: items
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSuccess(true);
      setError(null);
      
      // Reset form
      setSelectedLead('');
      setItems([{
        quantity: 1,
        tree_species: 'PINE',
        operation_type: 'FELLING',
        custom_operation: '',
        cost: 0
      }]);
      
    } catch (err) {
      console.error('Error creating quote:', err);
      setError('Failed to create quote. Please check your inputs and try again.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-green-500"></div>
          <p className="ml-4 text-gray-600">Loading leads data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 fade-in">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Skapa Offert</h1>
        <p className="mt-1 text-sm text-gray-500">Skapa en ny offert för en accepterad lead.</p>
      </header>

      {/* Error message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
          <p>{error}</p>
          <button 
            className="absolute top-0 bottom-0 right-0 px-4 py-3"
            onClick={() => setError(null)}
          >
            <span className="text-red-500 hover:text-red-700">&times;</span>
          </button>
        </div>
      )}

      {/* Success message */}
      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-6" role="alert">
          <p>Quote created successfully!</p>
          <button 
            className="absolute top-0 bottom-0 right-0 px-4 py-3"
            onClick={() => setSuccess(false)}
          >
            <span className="text-green-500 hover:text-green-700">&times;</span>
          </button>
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <form onSubmit={handleSubmit} className="px-4 py-5 sm:p-6">
          <div className="mb-6">
            <label htmlFor="lead" className="block text-sm font-medium text-gray-700 mb-1">Välj Lead</label>
            <select 
              id="lead"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md shadow-sm"
              value={selectedLead}
              onChange={(e) => setSelectedLead(e.target.value)}
              required
            >
              <option value="">-- Välj en lead --</option>
              {leads.map(lead => (
                <option key={lead.id} value={lead.id}>
                  {lead.customer_name} - {lead.address}, {lead.region}
                </option>
              ))}
            </select>
          </div>

          <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">Träd och Åtgärder</h3>
          <div className="overflow-x-auto mb-6">
            <table className="min-w-full divide-y divide-gray-200 border border-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Antal</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Trädslag</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Åtgärd</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kostnad (SEK)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Åtgärder</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {items.map((item, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input 
                        type="number" 
                        min="1"
                        className="mt-1 block w-20 pl-3 pr-1 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md shadow-sm"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value))}
                        required
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select 
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md shadow-sm"
                        value={item.tree_species}
                        onChange={(e) => handleItemChange(index, 'tree_species', e.target.value)}
                        required
                      >
                        <option value="PINE">Tall (Pine)</option>
                        <option value="SPRUCE">Gran (Spruce)</option>
                        <option value="OAK">Ek (Oak)</option>
                        <option value="BEECH">Bok (Beech)</option>
                        <option value="MAPLE">Lönn (Maple)</option>
                        <option value="ASH">Ask (Ash)</option>
                        <option value="ALDER">Al (Alder)</option>
                        <option value="BIRCH">Björk (Birch)</option>
                        <option value="LINDEN">Lind (Linden)</option>
                        <option value="BIRD_CHERRY">Hägg (Bird Cherry)</option>
                        <option value="ROWAN">Rönn (Rowan)</option>
                        <option value="CHERRY">Körsbär (Cherry)</option>
                        <option value="WALNUT">Valnöt (Walnut)</option>
                        <option value="POPLAR">Poppel (Poplar)</option>
                        <option value="PLANE">Platan (Plane)</option>
                        <option value="WILLOW">Pil (Willow)</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <select 
                        className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md shadow-sm"
                        value={item.operation_type}
                        onChange={(e) => handleItemChange(index, 'operation_type', e.target.value)}
                        required
                      >
                        <option value="DEAD_WOOD">Död veds beskärning</option>
                        <option value="FELLING">Trädfällning</option>
                        <option value="SECTION_FELLING">Sektionsfällning</option>
                        <option value="ADVANCED_SECTION_FELLING">Avancerad sektionsfällning</option>
                        <option value="CROWN_REDUCTION">Kronreducering</option>
                        <option value="MAINTENANCE_PRUNING">Underhållsbeskäring</option>
                        <option value="SPACE_PRUNING">Utrymmesbeskäring</option>
                        <option value="CROWN_LIFTING">Kronlyft</option>
                        <option value="POLLARDING">Hamling</option>
                        <option value="OTHER">Annat</option>
                        <option value="REMOVAL">Bortförsling</option>
                        <option value="THINNING">Urglesing</option>
                        <option value="STUMP_GRINDING">Stubbfräsning</option>
                        <option value="CROWN_STABILIZATION">Kronstabilisering</option>
                        <option value="EMERGENCY">Jour</option>
                      </select>
                      {item.operation_type === 'OTHER' && (
                        <input 
                          type="text"
                          placeholder="Beskriv åtgärd"
                          className="mt-2 block w-full pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md shadow-sm"
                          value={item.custom_operation}
                          onChange={(e) => handleItemChange(index, 'custom_operation', e.target.value)}
                          required
                        />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input 
                        type="number" 
                        min="0"
                        className="mt-1 block w-24 pl-3 pr-1 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md shadow-sm"
                        value={item.cost}
                        onChange={(e) => handleItemChange(index, 'cost', parseFloat(e.target.value))}
                        required
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {items.length > 1 && (
                        <button 
                          type="button"
                          className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-200"
                          onClick={() => handleRemoveRow(index)}
                        >
                          Ta bort
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button 
            type="button"
            className="mb-6 inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200"
            onClick={handleAddRow}
          >
            + Lägg till rad
          </button>

          <div className="text-right mb-6 space-y-1">
            <div className="text-lg font-medium text-gray-900">Totalt: {totalAmount.toFixed(2)} SEK</div>
            <div className="text-sm text-gray-500">Provision (10%): {commissionAmount.toFixed(2)} SEK</div>
          </div>

          <div className="flex justify-end space-x-3 border-t border-gray-200 pt-5">
            <Link to="/admin/dashboard" className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-200">
              Avbryt
            </Link>
            <button type="submit" className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200">
              Skapa Offert
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateQuote;
