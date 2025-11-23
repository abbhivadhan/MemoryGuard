/**
 * Data Validation Utilities
 * Validates data to ensure no placeholder or demo data is used
 * Requirements: 21.8
 */

// Common placeholder patterns to detect
const PLACEHOLDER_PATTERNS = [
  /demo/i,
  /test.*data/i,
  /placeholder/i,
  /sample/i,
  /fake/i,
  /mock/i,
  /example/i,
  /lorem.*ipsum/i,
  /xxx+/i,
  /\[.*\]/,  // [placeholder]
  /\{.*\}/,  // {placeholder}
];

// Common demo values
const DEMO_VALUES = [
  'demo',
  'test',
  'sample',
  'placeholder',
  'example',
  'fake',
  'mock',
  'N/A',
  'TBD',
  'TODO',
];

/**
 * Check if a string value appears to be placeholder/demo data
 */
export function isPlaceholderString(value: string): boolean {
  if (!value || typeof value !== 'string') {
    return false;
  }

  const normalized = value.trim().toLowerCase();

  // Check against demo values
  if (DEMO_VALUES.includes(normalized)) {
    return true;
  }

  // Check against patterns
  return PLACEHOLDER_PATTERNS.some(pattern => pattern.test(value));
}

/**
 * Check if a number appears to be a placeholder value
 */
export function isPlaceholderNumber(value: number): boolean {
  // Common placeholder numbers
  const placeholderNumbers = [
    0,
    -1,
    999,
    9999,
    99999,
    123,
    12345,
    111111,
    123456789,
  ];

  return placeholderNumbers.includes(value);
}

/**
 * Validate health metric data
 */
export interface HealthMetricData {
  name: string;
  value: number;
  type: string;
  unit?: string;
}

export function validateHealthMetric(metric: HealthMetricData): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // Check for placeholder strings
  if (isPlaceholderString(metric.name)) {
    errors.push(`Metric name "${metric.name}" appears to be placeholder data`);
  }

  if (metric.unit && isPlaceholderString(metric.unit)) {
    errors.push(`Metric unit "${metric.unit}" appears to be placeholder data`);
  }

  // Check for invalid values
  if (isNaN(metric.value) || !isFinite(metric.value)) {
    errors.push('Metric value must be a valid number');
  }

  // Check for placeholder numbers
  if (isPlaceholderNumber(metric.value)) {
    errors.push(`Metric value ${metric.value} appears to be placeholder data`);
  }

  // Type-specific validation
  if (metric.type === 'cognitive') {
    // Cognitive scores should be in reasonable ranges
    if (metric.name.toLowerCase().includes('mmse') && (metric.value < 0 || metric.value > 30)) {
      errors.push('MMSE score must be between 0 and 30');
    }
    if (metric.name.toLowerCase().includes('moca') && (metric.value < 0 || metric.value > 30)) {
      errors.push('MoCA score must be between 0 and 30');
    }
  }

  if (metric.type === 'biomarker') {
    // Biomarkers should be positive
    if (metric.value < 0) {
      errors.push('Biomarker values cannot be negative');
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate medication data
 */
export interface MedicationData {
  name: string;
  dosage: string;
  frequency: string;
}

export function validateMedication(medication: MedicationData): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // Check for placeholder strings
  if (isPlaceholderString(medication.name)) {
    errors.push(`Medication name "${medication.name}" appears to be placeholder data`);
  }

  if (isPlaceholderString(medication.dosage)) {
    errors.push(`Dosage "${medication.dosage}" appears to be placeholder data`);
  }

  if (isPlaceholderString(medication.frequency)) {
    errors.push(`Frequency "${medication.frequency}" appears to be placeholder data`);
  }

  // Check for empty values
  if (!medication.name || medication.name.trim().length === 0) {
    errors.push('Medication name is required');
  }

  if (!medication.dosage || medication.dosage.trim().length === 0) {
    errors.push('Dosage is required');
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Validate assessment data
 */
export interface AssessmentData {
  type: string;
  score: number;
  max_score: number;
}

export function validateAssessment(assessment: AssessmentData): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  // Check for placeholder values
  if (isPlaceholderNumber(assessment.score)) {
    errors.push(`Assessment score ${assessment.score} appears to be placeholder data`);
  }

  // Check score is within valid range
  if (assessment.score < 0 || assessment.score > assessment.max_score) {
    errors.push(`Score must be between 0 and ${assessment.max_score}`);
  }

  // Check for valid assessment type
  const validTypes = ['MMSE', 'MoCA', 'CDR', 'ClockDrawing'];
  if (!validTypes.includes(assessment.type)) {
    errors.push(`Invalid assessment type: ${assessment.type}`);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Log validation warnings
 */
export function logValidationWarning(
  dataType: string,
  data: any,
  errors: string[]
): void {
  console.warn(`[Data Validation] ${dataType} validation failed:`, {
    data,
    errors,
    timestamp: new Date().toISOString(),
  });

  // In production, this could send to a logging service
  if (import.meta.env.PROD) {
    // TODO: Send to logging service (e.g., Sentry, LogRocket)
  }
}

/**
 * Validate and log data before submission
 */
export function validateAndLog<T>(
  dataType: string,
  data: T,
  validator: (data: T) => { valid: boolean; errors: string[] }
): boolean {
  const result = validator(data);

  if (!result.valid) {
    logValidationWarning(dataType, data, result.errors);
    return false;
  }

  return true;
}

export default {
  isPlaceholderString,
  isPlaceholderNumber,
  validateHealthMetric,
  validateMedication,
  validateAssessment,
  logValidationWarning,
  validateAndLog,
};
