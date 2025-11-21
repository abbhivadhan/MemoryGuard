/**
 * Access Management Component
 * Allows patients to manage provider access and view audit logs
 */
import React, { useState, useEffect } from 'react';
import {
  getMyProviders,
  revokeProviderAccess,
  grantProviderAccess,
  getAccessLogs,
  ProviderAccessWithProvider,
  AccessLog,
} from '../../services/providerService';
import { Shield, UserCheck, Clock, Activity, Plus, Trash2, Eye } from 'lucide-react';

const AccessManagement: React.FC = () => {
  const [providers, setProviders] = useState<ProviderAccessWithProvider[]>([]);
  const [selectedAccess, setSelectedAccess] = useState<string | null>(null);
  const [accessLogs, setAccessLogs] = useState<AccessLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showGrantForm, setShowGrantForm] = useState(false);
  const [providerEmail, setProviderEmail] = useState('');

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMyProviders();
      setProviders(data);
    } catch (err: any) {
      console.error('Error loading providers:', err);
      setError(err.response?.data?.detail || 'Failed to load provider access');
    } finally {
      setLoading(false);
    }
  };

  const loadAccessLogs = async (accessId: string) => {
    try {
      const logs = await getAccessLogs(accessId);
      setAccessLogs(logs);
      setSelectedAccess(accessId);
    } catch (err: any) {
      console.error('Error loading access logs:', err);
      setError(err.response?.data?.detail || 'Failed to load access logs');
    }
  };

  const handleGrantAccess = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await grantProviderAccess({
        provider_email: providerEmail,
        can_view_assessments: true,
        can_view_health_metrics: true,
        can_view_medications: true,
        can_view_imaging: true,
        can_add_notes: true,
      });
      setProviderEmail('');
      setShowGrantForm(false);
      await loadProviders();
    } catch (err: any) {
      console.error('Error granting access:', err);
      setError(err.response?.data?.detail || 'Failed to grant provider access');
    }
  };

  const handleRevokeAccess = async (accessId: string, providerName: string) => {
    if (!confirm(`Are you sure you want to revoke access for ${providerName}?`)) {
      return;
    }

    try {
      setError(null);
      await revokeProviderAccess(accessId);
      await loadProviders();
      if (selectedAccess === accessId) {
        setSelectedAccess(null);
        setAccessLogs([]);
      }
    } catch (err: any) {
      console.error('Error revoking access:', err);
      setError(err.response?.data?.detail || 'Failed to revoke provider access');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/20 text-green-400 border-green-500';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500';
      case 'revoked':
        return 'bg-red-500/20 text-red-400 border-red-500';
      case 'expired':
        return 'bg-gray-500/20 text-gray-400 border-gray-500';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading provider access...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Shield className="w-10 h-10" />
            Provider Access Management
          </h1>
          <p className="text-gray-300">Manage healthcare provider access to your data</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-500/20 border border-red-500 rounded-lg p-4 text-red-400">
            {error}
          </div>
        )}

        {/* Grant Access Button */}
        <div className="mb-6">
          {!showGrantForm ? (
            <button
              onClick={() => setShowGrantForm(true)}
              className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
            >
              <Plus className="w-5 h-5" />
              Grant Provider Access
            </button>
          ) : (
            <form onSubmit={handleGrantAccess} className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4">Grant Provider Access</h3>
              <div className="flex gap-4">
                <input
                  type="email"
                  value={providerEmail}
                  onChange={(e) => setProviderEmail(e.target.value)}
                  placeholder="Provider email address"
                  required
                  className="flex-1 px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
                <button
                  type="submit"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg transition-colors font-medium"
                >
                  Grant Access
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowGrantForm(false);
                    setProviderEmail('');
                  }}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Provider Access List */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h2 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
              <UserCheck className="w-6 h-6" />
              Authorized Providers
            </h2>

            {providers.length > 0 ? (
              <div className="space-y-4">
                {providers.map((access) => (
                  <div
                    key={access.id}
                    className="bg-white/5 rounded-lg p-4 border border-white/10"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white">
                          {access.provider.name}
                        </h3>
                        <p className="text-sm text-gray-400">{access.provider.email}</p>
                        <p className="text-sm text-gray-400 capitalize">
                          {access.provider.provider_type.replace('_', ' ')}
                          {access.provider.institution && ` • ${access.provider.institution}`}
                        </p>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(access.status)}`}>
                        {access.status}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mb-3">
                      <div>Granted: {new Date(access.granted_at || access.created_at).toLocaleDateString()}</div>
                      {access.expires_at && (
                        <div>Expires: {new Date(access.expires_at).toLocaleDateString()}</div>
                      )}
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => loadAccessLogs(access.id)}
                        className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg transition-colors text-sm"
                      >
                        <Eye className="w-4 h-4" />
                        View Logs
                      </button>
                      {access.status === 'active' && (
                        <button
                          onClick={() => handleRevokeAccess(access.id, access.provider.name)}
                          className="flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg transition-colors text-sm"
                        >
                          <Trash2 className="w-4 h-4" />
                          Revoke
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <UserCheck className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">No providers yet</h3>
                <p className="text-gray-400">Grant access to healthcare providers to get started</p>
              </div>
            )}
          </div>

          {/* Access Logs */}
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
            <h2 className="text-2xl font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="w-6 h-6" />
              Access Audit Log
            </h2>

            {selectedAccess ? (
              accessLogs.length > 0 ? (
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {accessLogs.map((log) => (
                    <div
                      key={log.id}
                      className="bg-white/5 rounded-lg p-3 border border-white/10"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <div className="text-white font-medium capitalize">
                            {log.action.replace(/_/g, ' ')}
                          </div>
                          {log.resource_type && (
                            <div className="text-xs text-gray-400">
                              {log.resource_type}: {log.resource_id}
                            </div>
                          )}
                        </div>
                        <Clock className="w-4 h-4 text-gray-400" />
                      </div>
                      <div className="text-xs text-gray-400">
                        {new Date(log.created_at).toLocaleString()}
                      </div>
                      {log.ip_address && (
                        <div className="text-xs text-gray-500 mt-1">
                          IP: {log.ip_address}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400">No access logs yet</p>
                </div>
              )
            ) : (
              <div className="text-center py-12">
                <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-white mb-2">Select a provider</h3>
                <p className="text-gray-400">Click "View Logs" to see access history</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccessManagement;
