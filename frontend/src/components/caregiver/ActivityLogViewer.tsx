/**
 * Activity Log Viewer - Comprehensive activity log with filtering and search
 * 
 * Requirements: 6.5
 */
import React, { useEffect, useState } from 'react';
import { getPatientActivityLog, ActivityLog } from '../../services/caregiverService';

interface ActivityLogViewerProps {
  patientId: string;
  patientName: string;
}

const ActivityLogViewer: React.FC<ActivityLogViewerProps> = ({ patientId, patientName }) => {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [activityTypeFilter, setActivityTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange, setDateRange] = useState<'7days' | '30days' | '90days' | 'custom'>('30days');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    loadActivityLog();
  }, [patientId, dateRange, activityTypeFilter]);

  const loadActivityLog = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Calculate date range
      let start: string | undefined;
      let end: string | undefined;
      
      if (dateRange === 'custom') {
        start = startDate;
        end = endDate;
      } else {
        const now = new Date();
        end = now.toISOString();
        
        const daysAgo = dateRange === '7days' ? 7 : dateRange === '30days' ? 30 : 90;
        const startDate = new Date(now.getTime() - daysAgo * 24 * 60 * 60 * 1000);
        start = startDate.toISOString();
      }
      
      const data = await getPatientActivityLog(
        patientId,
        start,
        end,
        activityTypeFilter === 'all' ? undefined : activityTypeFilter
      );
      
      setLogs(data);
    } catch (err: any) {
      console.error('Error loading activity log:', err);
      setError(err.response?.data?.detail || 'Failed to load activity log');
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'routine':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        );
      case 'medication':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        );
      case 'assessment':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'reminder':
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
      case 'taken':
        return 'text-green-500 bg-green-900/30';
      case 'missed':
      case 'skipped':
        return 'text-red-500 bg-red-900/30';
      case 'pending':
        return 'text-yellow-500 bg-yellow-900/30';
      default:
        return 'text-gray-500 bg-gray-900/30';
    }
  };

  const getActivityTypeColor = (type: string) => {
    switch (type) {
      case 'routine':
        return 'text-blue-400';
      case 'medication':
        return 'text-purple-400';
      case 'assessment':
        return 'text-green-400';
      case 'reminder':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  // Filter logs based on search and status
  const filteredLogs = logs.filter(log => {
    if (statusFilter !== 'all' && log.status !== statusFilter) return false;
    if (searchQuery && !log.activity_name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !log.description.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    return true;
  });

  // Group logs by date
  const groupedLogs = filteredLogs.reduce((groups, log) => {
    const date = new Date(log.timestamp).toLocaleDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(log);
    return groups;
  }, {} as Record<string, ActivityLog[]>);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="text-white text-center">Loading activity log...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-red-700">
        <div className="text-red-500 text-center">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-2xl font-bold text-white mb-4">
          Activity Log - {patientName}
        </h2>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Search</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search activities..."
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm"
            />
          </div>

          {/* Activity Type */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Activity Type</label>
            <select
              value={activityTypeFilter}
              onChange={(e) => setActivityTypeFilter(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm"
            >
              <option value="all">All Types</option>
              <option value="routine">Routines</option>
              <option value="medication">Medications</option>
              <option value="assessment">Assessments</option>
              <option value="reminder">Reminders</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="taken">Taken</option>
              <option value="missed">Missed</option>
              <option value="skipped">Skipped</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-sm text-gray-400 mb-2">Date Range</label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as any)}
              className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm"
            >
              <option value="7days">Last 7 Days</option>
              <option value="30days">Last 30 Days</option>
              <option value="90days">Last 90 Days</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
        </div>

        {/* Custom Date Range */}
        {dateRange === 'custom' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-gray-700 text-white rounded px-3 py-2 text-sm"
              />
            </div>
          </div>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">Total Activities</div>
            <div className="text-xl font-bold text-white">{filteredLogs.length}</div>
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">Completed</div>
            <div className="text-xl font-bold text-green-500">
              {filteredLogs.filter(l => l.status === 'completed' || l.status === 'taken').length}
            </div>
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">Missed</div>
            <div className="text-xl font-bold text-red-500">
              {filteredLogs.filter(l => l.status === 'missed' || l.status === 'skipped').length}
            </div>
          </div>
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="text-gray-400 text-xs mb-1">Pending</div>
            <div className="text-xl font-bold text-yellow-500">
              {filteredLogs.filter(l => l.status === 'pending').length}
            </div>
          </div>
        </div>
      </div>

      {/* Activity Log */}
      {Object.keys(groupedLogs).length === 0 ? (
        <div className="bg-gray-800 rounded-lg p-12 text-center border border-gray-700">
          <div className="text-gray-400 text-lg">No activities found</div>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedLogs).map(([date, dayLogs]) => (
            <div key={date} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-bold text-white mb-4">{date}</h3>
              <div className="space-y-3">
                {dayLogs.map((log) => (
                  <div
                    key={log.id}
                    className="bg-gray-700 rounded-lg p-4 hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-start space-x-4">
                      <div className={`mt-1 ${getActivityTypeColor(log.activity_type)}`}>
                        {getActivityIcon(log.activity_type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-3">
                            <h4 className="font-semibold text-white">{log.activity_name}</h4>
                            <span className="px-2 py-1 bg-gray-600 text-gray-300 rounded text-xs">
                              {log.activity_type}
                            </span>
                            <span className={`px-2 py-1 rounded text-xs ${getStatusColor(log.status)}`}>
                              {log.status}
                            </span>
                          </div>
                          <div className="text-sm text-gray-400">
                            {new Date(log.timestamp).toLocaleTimeString()}
                          </div>
                        </div>
                        <p className="text-sm text-gray-300">{log.description}</p>
                        {log.metadata && Object.keys(log.metadata).length > 0 && (
                          <div className="mt-2 text-xs text-gray-500">
                            {Object.entries(log.metadata).map(([key, value]) => (
                              <span key={key} className="mr-4">
                                {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ActivityLogViewer;
