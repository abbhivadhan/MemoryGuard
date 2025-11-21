/**
 * Imaging Upload Component
 * Handles DICOM file upload and displays processing status
 */
import React, { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import {
  uploadImagingFile,
  pollImagingStatus,
  ImagingUploadResponse,
  ImagingAnalysis,
  ImagingProcessingStatus
} from '../../services/imagingService';

interface ImagingUploadProps {
  onUploadComplete?: (analysis: ImagingAnalysis) => void;
  onError?: (error: string) => void;
}

const ImagingUpload: React.FC<ImagingUploadProps> = ({
  onUploadComplete,
  onError
}) => {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadResponse, setUploadResponse] = useState<ImagingUploadResponse | null>(null);
  const [processingStatus, setProcessingStatus] = useState<ImagingProcessingStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileUpload = async (file: File) => {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.dcm') && !file.name.toLowerCase().endsWith('.dicom')) {
      const errorMsg = 'Please upload a DICOM file (.dcm or .dicom)';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      return;
    }

    // Validate file size (100MB limit)
    if (file.size > 100 * 1024 * 1024) {
      const errorMsg = 'File size exceeds 100MB limit';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      return;
    }

    setError(null);
    setUploading(true);

    try {
      // Upload file
      const response = await uploadImagingFile(file);
      setUploadResponse(response);
      setUploading(false);
      setProcessing(true);

      // Poll for processing completion
      const analysis = await pollImagingStatus(
        response.id,
        (status) => {
          setProcessingStatus(status);
        }
      );

      setProcessing(false);
      if (onUploadComplete) {
        onUploadComplete(analysis);
      }
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to upload imaging file';
      setError(errorMsg);
      if (onError) onError(errorMsg);
      setUploading(false);
      setProcessing(false);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      {/* Upload Area */}
      {!uploading && !processing && !uploadResponse && (
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold mb-2">Upload Brain MRI Scan</h3>
          <p className="text-gray-600 mb-4">
            Drag and drop your DICOM file here, or click to browse
          </p>
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".dcm,.dicom"
            onChange={handleFileInput}
          />
          <label
            htmlFor="file-upload"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
          >
            Select DICOM File
          </label>
          <p className="text-xs text-gray-500 mt-4">
            Supported formats: .dcm, .dicom (Max size: 100MB)
          </p>
        </div>
      )}

      {/* Uploading Status */}
      {uploading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <Loader className="w-12 h-12 mx-auto mb-4 text-blue-600 animate-spin" />
          <h3 className="text-lg font-semibold mb-2">Uploading...</h3>
          <p className="text-gray-600">Encrypting and uploading your imaging file</p>
        </div>
      )}

      {/* Processing Status */}
      {processing && processingStatus && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Loader className="w-6 h-6 text-purple-600 animate-spin" />
              <div>
                <h3 className="text-lg font-semibold">Processing MRI Data</h3>
                <p className="text-sm text-gray-600">{processingStatus.message}</p>
              </div>
            </div>
            <span className="text-2xl font-bold text-purple-600">
              {processingStatus.progress}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${processingStatus.progress}%` }}
            ></div>
          </div>
          <div className="mt-4 text-sm text-gray-600">
            <ul className="space-y-1">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                Parsing DICOM metadata
              </li>
              <li className="flex items-center gap-2">
                {processingStatus.progress && processingStatus.progress > 30 ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <Loader className="w-4 h-4 text-gray-400 animate-spin" />
                )}
                Extracting volumetric measurements
              </li>
              <li className="flex items-center gap-2">
                {processingStatus.progress && processingStatus.progress > 60 ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <Loader className="w-4 h-4 text-gray-400 animate-spin" />
                )}
                Detecting atrophy patterns
              </li>
              <li className="flex items-center gap-2">
                {processingStatus.progress && processingStatus.progress > 90 ? (
                  <CheckCircle className="w-4 h-4 text-green-600" />
                ) : (
                  <Loader className="w-4 h-4 text-gray-400 animate-spin" />
                )}
                Generating ML features
              </li>
            </ul>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-1">Upload Failed</h3>
              <p className="text-red-700">{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  setUploadResponse(null);
                  setProcessingStatus(null);
                }}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImagingUpload;
