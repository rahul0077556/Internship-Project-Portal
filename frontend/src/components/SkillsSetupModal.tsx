import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiCheck } from 'react-icons/fi';
import { studentService } from '../services/studentService';
import './SkillsSetupModal.css';

interface SkillsSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

const SkillsSetupModal: React.FC<SkillsSetupModalProps> = ({ isOpen, onClose, onComplete }) => {
  const [allSkills, setAllSkills] = useState<any[]>([]);
  const [selectedTechnical, setSelectedTechnical] = useState<string[]>([]);
  const [selectedNonTechnical, setSelectedNonTechnical] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTech, setSearchTech] = useState('');
  const [searchNonTech, setSearchNonTech] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadSkills();
    }
  }, [isOpen]);

  const loadSkills = async () => {
    try {
      const data = await studentService.getSkills();
      setAllSkills(data.all_skills || []);
      
      // Pre-select existing skills
      const tech = (data.technical_skills || []).map((s: any) => s.skill_name || s.name);
      const nonTech = (data.non_technical_skills || []).map((s: any) => s.skill_name || s.name);
      setSelectedTechnical(tech);
      setSelectedNonTechnical(nonTech);
    } catch (error) {
      console.error('Failed to load skills:', error);
    }
  };

  const toggleTechnicalSkill = (skillName: string) => {
    setSelectedTechnical(prev =>
      prev.includes(skillName)
        ? prev.filter(s => s !== skillName)
        : [...prev, skillName]
    );
  };

  const toggleNonTechnicalSkill = (skillName: string) => {
    setSelectedNonTechnical(prev =>
      prev.includes(skillName)
        ? prev.filter(s => s !== skillName)
        : [...prev, skillName]
    );
  };

  const handleSave = async () => {
    if (selectedTechnical.length === 0 && selectedNonTechnical.length === 0) {
      alert('Please select at least one skill');
      return;
    }

    setLoading(true);
    try {
      await studentService.updateSkills({
        technical_skills: selectedTechnical,
        non_technical_skills: selectedNonTechnical
      });
      onComplete();
      onClose();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to save skills');
    } finally {
      setLoading(false);
    }
  };

  const technicalSkills = allSkills.filter(s => 
    s.category && ['programming', 'framework', 'database', 'cloud', 'devops', 'mobile', 'data-science', 'web', 'library'].includes(s.category)
  );
  
  const nonTechnicalSkills = allSkills.filter(s => 
    !s.category || !['programming', 'framework', 'database', 'cloud', 'devops', 'mobile', 'data-science', 'web', 'library'].includes(s.category)
  );

  const filteredTechnical = technicalSkills.filter(s =>
    s.name.toLowerCase().includes(searchTech.toLowerCase())
  );

  const filteredNonTechnical = nonTechnicalSkills.filter(s =>
    s.name.toLowerCase().includes(searchNonTech.toLowerCase())
  );

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="skills-modal-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="skills-modal-content"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="skills-modal-header">
              <h2>Add Your Skills</h2>
              <p>Select your technical and non-technical skills to get matched with opportunities</p>
              <button className="close-button" onClick={onClose}>
                <FiX size={24} />
              </button>
            </div>

            <div className="skills-modal-body">
              {/* Technical Skills */}
              <div className="skills-section">
                <h3>Technical Skills</h3>
                <input
                  type="text"
                  placeholder="Search technical skills..."
                  value={searchTech}
                  onChange={(e) => setSearchTech(e.target.value)}
                  className="skills-search"
                />
                <div className="skills-grid">
                  {filteredTechnical.map((skill) => (
                    <motion.button
                      key={skill.id}
                      className={`skill-chip ${selectedTechnical.includes(skill.name) ? 'selected' : ''}`}
                      onClick={() => toggleTechnicalSkill(skill.name)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {skill.name}
                      {selectedTechnical.includes(skill.name) && (
                        <FiCheck size={16} className="check-icon" />
                      )}
                    </motion.button>
                  ))}
                </div>
                {selectedTechnical.length > 0 && (
                  <div className="selected-skills-preview">
                    <strong>Selected ({selectedTechnical.length}):</strong>
                    <div className="selected-chips">
                      {selectedTechnical.map(skill => (
                        <span key={skill} className="selected-chip">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Non-Technical Skills */}
              <div className="skills-section">
                <h3>Non-Technical Skills</h3>
                <input
                  type="text"
                  placeholder="Search non-technical skills..."
                  value={searchNonTech}
                  onChange={(e) => setSearchNonTech(e.target.value)}
                  className="skills-search"
                />
                <div className="skills-grid">
                  {filteredNonTechnical.map((skill) => (
                    <motion.button
                      key={skill.id}
                      className={`skill-chip ${selectedNonTechnical.includes(skill.name) ? 'selected' : ''}`}
                      onClick={() => toggleNonTechnicalSkill(skill.name)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {skill.name}
                      {selectedNonTechnical.includes(skill.name) && (
                        <FiCheck size={16} className="check-icon" />
                      )}
                    </motion.button>
                  ))}
                </div>
                {selectedNonTechnical.length > 0 && (
                  <div className="selected-skills-preview">
                    <strong>Selected ({selectedNonTechnical.length}):</strong>
                    <div className="selected-chips">
                      {selectedNonTechnical.map(skill => (
                        <span key={skill} className="selected-chip">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="skills-modal-footer">
              <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
                Skip for Now
              </button>
              <motion.button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={loading || (selectedTechnical.length === 0 && selectedNonTechnical.length === 0)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? 'Saving...' : `Save Skills (${selectedTechnical.length + selectedNonTechnical.length})`}
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default SkillsSetupModal;

