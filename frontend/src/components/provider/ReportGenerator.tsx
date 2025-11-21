/**
 * Report Generator Component
 * Generates comprehensive clinical reports for patients
 */
import React, { useState } from 'react';
import { FileText, Download, Loader } from 'lucide-react';
import api from '../../services/api';

interface ReportGeneratorProps {
  patientId: string;
  patientName: string;
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({ patientId, patientName }) => {
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateReport = async () => {
    try {
      setGenerating(true);
      setError(null);

      // Fetch report data from backend
      const response = await api.get(`/providers/patients/${patientId}/report`);
      const reportData = response.data;

      // Generate HTML report
      const htmlContent = generateHTMLReport(reportData);

      // Create a blob and download
      const blob = new Blob([htmlContent], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `clinical-report-${patientName.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      console.error('Error generating report:', err);
      setError(err.response?.data?.detail || 'Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  const generateHTMLReport = (data: any): string => {
    const { generated_at, generated_by, patient, assessments, health_metrics, medications, predictions, clinical_notes } = data;

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clinical Report - ${patient.name}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .report-container {
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 3px solid #6366f1;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            color: #6366f1;
            margin: 0 0 10px 0;
        }
        .meta-info {
            color: #666;
            font-size: 14px;
        }
        .section {
            margin-bottom: 30px;
        }
        h2 {
            color: #4f46e5;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .patient-info {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        .info-item {
            padding: 8px 0;
        }
        .info-label {
            font-weight: bold;
            color: #4b5563;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f3f4f6;
            font-weight: bold;
            color: #374151;
        }
        .note-card {
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #6366f1;
        }
        .note-title {
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 5px;
        }
        .note-meta {
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 10px;
        }
        .note-content {
            color: #374151;
            white-space: pre-wrap;
        }
        .risk-score {
            font-size: 24px;
            font-weight: bold;
            color: #dc2626;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
        }
        @media print {
            body {
                background: white;
            }
            .report-container {
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>Clinical Report</h1>
            <div class="meta-info">
                <p><strong>Generated:</strong> ${new Date(generated_at).toLocaleString()}</p>
                <p><strong>Provider:</strong> ${generated_by.name} (${generated_by.provider_type})</p>
                ${generated_by.institution ? `<p><strong>Institution:</strong> ${generated_by.institution}</p>` : ''}
            </div>
        </div>

        <div class="section">
            <h2>Patient Information</h2>
            <div class="patient-info">
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Name:</span> ${patient.name}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span> ${patient.email}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Date of Birth:</span> ${patient.date_of_birth ? new Date(patient.date_of_birth).toLocaleDateString() : 'Not provided'}
                    </div>
                    <div class="info-item">
                        <span class="info-label">APOE Genotype:</span> ${patient.apoe_genotype || 'Not tested'}
                    </div>
                    <div class="info-item">
                        <span class="info-label">Last Active:</span> ${new Date(patient.last_active).toLocaleString()}
                    </div>
                </div>
            </div>
        </div>

        ${predictions.length > 0 ? `
        <div class="section">
            <h2>Risk Assessment Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Risk Score</th>
                        <th>Category</th>
                        <th>6-Month</th>
                        <th>12-Month</th>
                        <th>24-Month</th>
                    </tr>
                </thead>
                <tbody>
                    ${predictions.map((p: any) => `
                    <tr>
                        <td>${new Date(p.created_at).toLocaleDateString()}</td>
                        <td class="risk-score">${(p.risk_score * 100).toFixed(1)}%</td>
                        <td>${p.risk_category}</td>
                        <td>${p.six_month_forecast ? (p.six_month_forecast * 100).toFixed(1) + '%' : 'N/A'}</td>
                        <td>${p.twelve_month_forecast ? (p.twelve_month_forecast * 100).toFixed(1) + '%' : 'N/A'}</td>
                        <td>${p.twenty_four_month_forecast ? (p.twenty_four_month_forecast * 100).toFixed(1) + '%' : 'N/A'}</td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ` : ''}

        ${assessments.length > 0 ? `
        <div class="section">
            <h2>Cognitive Assessments</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Test Type</th>
                        <th>Score</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
                    ${assessments.map((a: any) => `
                    <tr>
                        <td>${new Date(a.completed_at).toLocaleDateString()}</td>
                        <td>${a.test_type}</td>
                        <td>${a.total_score}/${a.max_score}</td>
                        <td>${Math.round(a.duration_seconds / 60)} minutes</td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ` : ''}

        ${medications.length > 0 ? `
        <div class="section">
            <h2>Medications</h2>
            <table>
                <thead>
                    <tr>
                        <th>Medication</th>
                        <th>Dosage</th>
                        <th>Frequency</th>
                        <th>Status</th>
                        <th>Side Effects</th>
                    </tr>
                </thead>
                <tbody>
                    ${medications.map((m: any) => `
                    <tr>
                        <td>${m.name}</td>
                        <td>${m.dosage}</td>
                        <td>${m.frequency}</td>
                        <td>${m.is_active ? 'Active' : 'Inactive'}</td>
                        <td>${m.side_effects && m.side_effects.length > 0 ? m.side_effects.join(', ') : 'None reported'}</td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ` : ''}

        ${health_metrics.length > 0 ? `
        <div class="section">
            <h2>Health Metrics (Recent)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody>
                    ${health_metrics.slice(0, 20).map((m: any) => `
                    <tr>
                        <td>${new Date(m.recorded_at).toLocaleDateString()}</td>
                        <td>${m.metric_name}</td>
                        <td>${m.value} ${m.unit}</td>
                        <td>${m.source}</td>
                    </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        ` : ''}

        ${clinical_notes.length > 0 ? `
        <div class="section">
            <h2>Clinical Notes</h2>
            ${clinical_notes.map((note: any) => `
            <div class="note-card">
                <div class="note-title">${note.title}</div>
                <div class="note-meta">
                    ${note.note_type ? note.note_type.replace('_', ' ').toUpperCase() : 'NOTE'} | 
                    ${new Date(note.created_at).toLocaleString()} | 
                    ${note.provider_name}
                    ${note.is_private ? ' | PRIVATE' : ''}
                </div>
                <div class="note-content">${note.content}</div>
            </div>
            `).join('')}
        </div>
        ` : ''}

        <div class="footer">
            <p>This report is confidential and intended for healthcare professionals only.</p>
        </div>
    </div>
</body>
</html>
    `;
  };

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-white flex items-center gap-2 mb-2">
            <FileText className="w-5 h-5" />
            Clinical Report
          </h3>
          <p className="text-sm text-gray-300">
            Generate a comprehensive clinical report including all patient data
          </p>
        </div>
        <button
          onClick={generateReport}
          disabled={generating}
          className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg transition-colors font-medium"
        >
          {generating ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Download className="w-5 h-5" />
              Generate Report
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="mt-4 bg-red-500/20 border border-red-500 rounded-lg p-3 text-red-400 text-sm">
          {error}
        </div>
      )}
    </div>
  );
};

export default ReportGenerator;
