import { useState } from 'react';

interface PrivacySettingsProps {
  isAnonymous: boolean;
  visibility: 'public' | 'members_only' | 'matched_users';
  onAnonymousChange: (value: boolean) => void;
  onVisibilityChange: (value: 'public' | 'members_only' | 'matched_users') => void;
}

export default function PrivacySettings({
  isAnonymous,
  visibility,
  onAnonymousChange,
  onVisibilityChange,
}: PrivacySettingsProps) {
  const [showInfo, setShowInfo] = useState(false);

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Privacy Settings</h3>
        <button
          onClick={() => setShowInfo(!showInfo)}
          className="text-blue-600 hover:text-blue-700"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>

      {showInfo && (
        <div className="mb-4 p-3 bg-white rounded-lg text-sm text-gray-700">
          <p className="mb-2">
            <strong>Anonymous Posting:</strong> Your name will be hidden and shown as "Anonymous User"
          </p>
          <p className="mb-2">
            <strong>Public:</strong> Everyone can see your post
          </p>
          <p className="mb-2">
            <strong>Members Only:</strong> Only registered users can see your post
          </p>
          <p>
            <strong>Matched Users:</strong> Only users with similar profiles can see your post
          </p>
        </div>
      )}

      {/* Anonymous posting */}
      <div className="mb-4">
        <label className="flex items-start cursor-pointer">
          <input
            type="checkbox"
            checked={isAnonymous}
            onChange={(e) => onAnonymousChange(e.target.checked)}
            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 mt-0.5"
          />
          <div className="ml-3">
            <span className="text-sm font-medium text-gray-900">Post Anonymously</span>
            <p className="text-xs text-gray-600 mt-1">
              Your identity will be hidden from other users
            </p>
          </div>
        </label>
      </div>

      {/* Visibility settings */}
      <div>
        <label className="block text-sm font-medium text-gray-900 mb-2">
          Who can see this post?
        </label>
        <div className="space-y-2">
          <label className="flex items-start cursor-pointer">
            <input
              type="radio"
              name="visibility"
              value="public"
              checked={visibility === 'public'}
              onChange={(e) => onVisibilityChange(e.target.value as any)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 mt-0.5"
            />
            <div className="ml-3">
              <span className="text-sm font-medium text-gray-900">Public</span>
              <p className="text-xs text-gray-600">Everyone can see this post</p>
            </div>
          </label>

          <label className="flex items-start cursor-pointer">
            <input
              type="radio"
              name="visibility"
              value="members_only"
              checked={visibility === 'members_only'}
              onChange={(e) => onVisibilityChange(e.target.value as any)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 mt-0.5"
            />
            <div className="ml-3">
              <span className="text-sm font-medium text-gray-900">Members Only</span>
              <p className="text-xs text-gray-600">Only registered users can see this</p>
            </div>
          </label>

          <label className="flex items-start cursor-pointer">
            <input
              type="radio"
              name="visibility"
              value="matched_users"
              checked={visibility === 'matched_users'}
              onChange={(e) => onVisibilityChange(e.target.value as any)}
              className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 mt-0.5"
            />
            <div className="ml-3">
              <span className="text-sm font-medium text-gray-900">Matched Users Only</span>
              <p className="text-xs text-gray-600">
                Only users with similar risk profiles or disease stages
              </p>
            </div>
          </label>
        </div>
      </div>

      {/* Privacy notice */}
      <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex gap-2">
          <svg className="w-5 h-5 text-yellow-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-xs text-yellow-800">
            Even with privacy settings, please avoid sharing sensitive personal information like full names, addresses, or medical record numbers.
          </p>
        </div>
      </div>
    </div>
  );
}
