/**
 * Clinical Notes Component
 * Allows providers to create and view clinical notes for patients
 */
import React, { useState, useEffect } from 'react';
import {
  getPatientNotes,
  createClinicalNote,
  updateClinicalNote,
  deleteClinicalNote,
  ClinicalNoteWithProvider,
} from '../../services/providerService';
import { FileText, Plus, Edit2, Trash2, Save, X, Lock } from 'lucide-react';

interface ClinicalNotesProps {
  patientId: string;
}

const ClinicalNotes: React.FC<ClinicalNotesProps> = ({ patientId }) => {
  const [notes, setNotes] = useState<ClinicalNoteWithProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingNote, setEditingNote] = useState<ClinicalNoteWithProvider | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    note_type: 'progress_note',
    is_private: false,
  });

  useEffect(() => {
    loadNotes();
  }, [patientId]);

  const loadNotes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPatientNotes(patientId);
      setNotes(data);
    } catch (err: any) {
      console.error('Error loading notes:', err);
      setError(err.response?.data?.detail || 'Failed to load clinical notes');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editingNote) {
        // Update existing note
        await updateClinicalNote(editingNote.id, formData);
      } else {
        // Create new note
        await createClinicalNote({
          patient_id: patientId,
          ...formData,
        });
      }

      // Reset form and reload notes
      setFormData({
        title: '',
        content: '',
        note_type: 'progress_note',
        is_private: false,
      });
      setShowForm(false);
      setEditingNote(null);
      await loadNotes();
    } catch (err: any) {
      console.error('Error saving note:', err);
      setError(err.response?.data?.detail || 'Failed to save clinical note');
    }
  };

  const handleEdit = (note: ClinicalNoteWithProvider) => {
    setEditingNote(note);
    setFormData({
      title: note.title,
      content: note.content,
      note_type: note.note_type || 'progress_note',
      is_private: note.is_private,
    });
    setShowForm(true);
  };

  const handleDelete = async (noteId: string) => {
    if (!confirm('Are you sure you want to delete this note?')) {
      return;
    }

    try {
      await deleteClinicalNote(noteId);
      await loadNotes();
    } catch (err: any) {
      console.error('Error deleting note:', err);
      setError(err.response?.data?.detail || 'Failed to delete clinical note');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingNote(null);
    setFormData({
      title: '',
      content: '',
      note_type: 'progress_note',
      is_private: false,
    });
  };

  if (loading) {
    return (
      <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
        <div className="text-white text-center">Loading clinical notes...</div>
      </div>
    );
  }

  return (
    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-semibold text-white flex items-center gap-2">
          <FileText className="w-6 h-6" />
          Clinical Notes
        </h3>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Note
          </button>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 bg-red-500/20 border border-red-500 rounded-lg p-3 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Note Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 bg-white/5 rounded-lg p-4 border border-white/10">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter note title"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Note Type
              </label>
              <select
                value={formData.note_type}
                onChange={(e) => setFormData({ ...formData, note_type: e.target.value })}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="progress_note">Progress Note</option>
                <option value="assessment">Assessment</option>
                <option value="treatment_plan">Treatment Plan</option>
                <option value="consultation">Consultation</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Content *
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                required
                rows={6}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                placeholder="Enter clinical note content"
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_private"
                checked={formData.is_private}
                onChange={(e) => setFormData({ ...formData, is_private: e.target.checked })}
                className="w-4 h-4 rounded border-white/20 bg-white/10 text-purple-600 focus:ring-purple-500"
              />
              <label htmlFor="is_private" className="text-sm text-gray-300 flex items-center gap-1">
                <Lock className="w-3 h-3" />
                Private note (only visible to you)
              </label>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Save className="w-4 h-4" />
                {editingNote ? 'Update Note' : 'Save Note'}
              </button>
              <button
                type="button"
                onClick={handleCancel}
                className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <X className="w-4 h-4" />
                Cancel
              </button>
            </div>
          </div>
        </form>
      )}

      {/* Notes List */}
      {notes.length > 0 ? (
        <div className="space-y-4">
          {notes.map((note) => (
            <div
              key={note.id}
              className="bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="text-lg font-semibold text-white">{note.title}</h4>
                    {note.is_private && (
                      <Lock className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                  <div className="flex items-center gap-3 text-sm text-gray-400">
                    <span className="capitalize">{note.note_type?.replace('_', ' ')}</span>
                    <span>•</span>
                    <span>{new Date(note.created_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>{note.provider.name}</span>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleEdit(note)}
                    className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg transition-colors"
                    title="Edit note"
                  >
                    <Edit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(note.id)}
                    className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                    title="Delete note"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-gray-300 whitespace-pre-wrap">{note.content}</p>
              {note.updated_at !== note.created_at && (
                <div className="mt-2 text-xs text-gray-500">
                  Last updated: {new Date(note.updated_at).toLocaleString()}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h4 className="text-lg font-semibold text-white mb-2">No clinical notes yet</h4>
          <p className="text-gray-400">Add your first clinical note to get started</p>
        </div>
      )}
    </div>
  );
};

export default ClinicalNotes;
