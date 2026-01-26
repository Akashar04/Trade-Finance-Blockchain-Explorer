import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { documentsAPI } from '../services/api';

export default function UploadDocumentPage() {
  const [formData, setFormData] = useState({
    doc_number: '',
    seller_id: '',
    file: null,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'file') {
      setFormData((prev) => ({ ...prev, file: files[0] }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.doc_number || !formData.seller_id || !formData.file) {
      setError('All fields are required');
      return;
    }

    setLoading(true);

    try {
      const form = new FormData();
      form.append('doc_number', formData.doc_number);
      form.append('seller_id', formData.seller_id);
      form.append('file', formData.file);

      // eslint-disable-next-line no-unused-vars
      const response = await documentsAPI.upload(form);
      alert('Document uploaded successfully!');
      navigate('/documents');
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Upload Document</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-700 font-bold mb-2">Document Number</label>
            <input
              type="text"
              name="doc_number"
              value={formData.doc_number}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., PO-2024-001"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-bold mb-2">Seller ID</label>
            <input
              type="number"
              name="seller_id"
              value={formData.seller_id}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="User ID of the seller"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 font-bold mb-2">File</label>
            <input
              type="file"
              name="file"
              onChange={handleChange}
              accept=".pdf,.doc,.docx"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
            <p className="text-sm text-gray-600 mt-2">Accepted formats: PDF, DOC, DOCX</p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded-lg"
          >
            {loading ? 'Uploading...' : 'Upload Document'}
          </button>
        </form>
      </div>
    </div>
  );
}
