import { useState, useEffect } from 'react';
import communityService, { UserMatch } from '../../services/communityService';

export default function UserMatching() {
  const [matches, setMatches] = useState<UserMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      setLoading(true);
      const data = await communityService.getMatchedUsers();
      setMatches(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load matches');
    } finally {
      setLoading(false);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-gray-400';
  };

  const getMatchScoreLabel = (score: number) => {
    if (score >= 0.7) return 'High Match';
    if (score >= 0.5) return 'Good Match';
    return 'Moderate Match';
  };

  if (loading) {
    return (
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6">
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        <h2 className="text-2xl font-bold text-gray-900">Matched Users</h2>
      </div>

      <p className="text-gray-400 mb-6">
        Connect with users who have similar experiences, risk profiles, or disease stages.
      </p>

      {matches.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p className="text-lg mb-2">No matches found yet</p>
          <p className="text-sm">
            Complete your risk assessment and cognitive tests to find users with similar profiles.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <div
              key={match.user_id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">Community Member</p>
                    <p className="text-sm text-gray-500">User ID: {match.user_id.slice(0, 8)}...</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${getMatchScoreColor(match.match_score)}`}>
                    {Math.round(match.match_score * 100)}%
                  </p>
                  <p className="text-xs text-gray-500">{getMatchScoreLabel(match.match_score)}</p>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-300">Match Reasons:</p>
                <div className="flex flex-wrap gap-2">
                  {match.match_reasons.map((reason, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                    >
                      {reason}
                    </span>
                  ))}
                </div>
              </div>

              {(match.risk_profile_similarity !== undefined || match.disease_stage_match !== undefined) && (
                <div className="mt-3 pt-3 border-t border-gray-200 flex gap-4 text-sm">
                  {match.risk_profile_similarity !== undefined && (
                    <div className="flex items-center gap-1 text-gray-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      Risk similarity: {Math.round(match.risk_profile_similarity * 100)}%
                    </div>
                  )}
                  {match.disease_stage_match && (
                    <div className="flex items-center gap-1 text-green-600">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Similar disease stage
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex gap-2">
          <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">Privacy Note</p>
            <p>
              User identities are protected. Matches are based on anonymized health data and risk profiles.
              You can connect through the forum while maintaining your privacy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
