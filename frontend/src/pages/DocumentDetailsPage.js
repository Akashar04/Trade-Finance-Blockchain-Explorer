import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function DocumentDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [document, setDocument] = useState(null);
  const [ledgerEntries, setLedgerEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [performingAction, setPerformingAction] = useState(null);

  const userRole = user?.role || '';

  useEffect(() => {
    fetchDocumentDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const fetchDocumentDetails = async () => {
    try {
      setLoading(true);
      const response = await documentsAPI.getDocumentDetails(id);
      setDocument(response.data);
      setLedgerEntries(response.data.ledger_entries || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch document details');
    } finally {
      setLoading(false);
    }
  };

  const handlePerformAction = async (action) => {
    setPerformingAction(action);
    try {
      await documentsAPI.performAction({
        doc_id: parseInt(id),
        action: action,
      });
      alert(`Action "${action}" performed successfully`);
      await fetchDocumentDetails();
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to perform action: ${action}`);
    } finally {
      setPerformingAction(null);
    }
  };

  const handleDownloadFile = async () => {
    try {
      const response = await documentsAPI.downloadFile(document.file_url);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.file_url);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      setError('Failed to download file');
    }
  };

  // Role-based available actions
  const getAvailableActions = () => {
    if (!document || !userRole) return [];

    const roleActionsMapping = {
      buyer: {
        PO: ['AMEND'],
        BOL: ['RECEIVED'],
      },
      seller: {
        BOL: ['SHIPPED', 'ISSUE_INVOICE'],
        PO: ['ISSUE_BOL'],
        LOC: ['ISSUE_BOL'], // Can issue BOL after LOC is issued
        INVOICE: [], // End of seller flow usually
      },
      auditor: {
        PO: ['VERIFY'],
        LOC: ['VERIFY'],
      },
      bank: {
        INVOICE: ['PAID'],
        PO: ['ISSUE_LOC'],
        LOC: ['ISSUE_LOC'], // Re-issue or confirm
      },
    };

    const roleActions = roleActionsMapping[userRole] || {};
    return roleActions[document.doc_type] || [];
  };

  const availableActions = getAvailableActions();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading document details...</div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">Document not found</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={() => navigate('/documents')}
        className="mb-6 text-blue-600 hover:text-blue-900"
      >
        ← Back to Documents
      </button>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Document Details */}
      <div className="bg-white rounded-lg shadow p-8 mb-6">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">{document.doc_number}</h1>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <p className="text-gray-600 text-sm">Document Type</p>
            <p className="text-lg font-semibold text-gray-900">
              <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                {document.doc_type}
              </span>
            </p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Created</p>
            <p className="text-lg font-semibold text-gray-900">
              {new Date(document.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        <div className="mb-6">
          <p className="text-gray-600 text-sm">SHA-256 Hash</p>
          <p className="font-mono text-sm break-all bg-gray-100 p-3 rounded">
            {document.hash}
          </p>
        </div>

        <div className="flex gap-4">
          <button
            onClick={handleDownloadFile}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
          >
            Download File
          </button>
        </div>
      </div>

      {/* Available Actions */}
      {availableActions.length > 0 && (
        <div className="bg-white rounded-lg shadow p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Available Actions</h2>
          <div className="flex flex-wrap gap-4">
            {availableActions.map((action) => (
              <button
                key={action}
                onClick={() => handlePerformAction(action)}
                disabled={performingAction === action}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
              >
                {performingAction === action ? `${action}...` : action}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Ledger Timeline */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Document Timeline</h2>

        {ledgerEntries.length === 0 ? (
          <p className="text-gray-600">No ledger entries yet</p>
        ) : (
          <div className="space-y-6">
            {ledgerEntries.map((entry, index) => (
              <div key={entry.id} className="flex">
                <div className="flex flex-col items-center mr-6">
                  <div className="bg-blue-600 text-white rounded-full h-10 w-10 flex items-center justify-center font-bold">
                    {index + 1}
                  </div>
                  {index < ledgerEntries.length - 1 && (
                    <div className="w-1 h-12 bg-gray-300 mt-2"></div>
                  )}
                </div>
                <div className="pb-6">
                  <p className="text-lg font-bold text-gray-900">{entry.action}</p>
                  <p className="text-sm text-gray-600">
                    {new Date(entry.created_at).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">Actor ID: {entry.actor_id}</p>
                  {entry.entry_metadata && (
                    <p className="text-sm text-gray-700 mt-2 font-mono bg-gray-100 p-2 rounded">
                      {entry.entry_metadata}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
