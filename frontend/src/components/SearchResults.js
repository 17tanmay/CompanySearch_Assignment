import React, { useState } from 'react';
import { Building2, Globe, MapPin, Calendar, Users, Tag, Plus, X } from 'lucide-react';
import { addTagToCompany, removeTagFromCompany, getTags } from '../services/api';

const SearchResults = ({ 
  results, 
  total, 
  loading, 
  error, 
  sortBy, 
  page, 
  totalPages, 
  onSortChange, 
  onPageChange 
}) => {
  if (loading) {
    return (
      <div className="results-panel">
        <div className="loading">
          <div className="loading-spinner"></div>
          Searching companies...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="results-panel">
        <div className="error">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="results-panel">
      <div className="search-header">
        <div className="search-results-title">
          Search Results ({total.toLocaleString()} found)
        </div>
        
        <div className="sort-controls">
          <span className="sort-label">Sort by:</span>
          <div className="sort-options">
            <button
              className={`sort-option ${sortBy === 'relevance' ? 'active' : ''}`}
              onClick={() => onSortChange('relevance')}
            >
              Relevance
            </button>
            <button
              className={`sort-option ${sortBy === 'name' ? 'active' : ''}`}
              onClick={() => onSortChange('name')}
            >
              Name
            </button>
            <button
              className={`sort-option ${sortBy === 'size' ? 'active' : ''}`}
              onClick={() => onSortChange('size')}
            >
              Size
            </button>
          </div>
        </div>
      </div>

      {results.length === 0 ? (
        <div className="no-results">
          <Building2 size={48} className="no-results-icon" />
          <h3>No companies found</h3>
          <p>Try adjusting your search criteria or filters</p>
        </div>
      ) : (
        <>
        <div className="results-list">
          {(results || []).map((company) => (
            <CompanyCard key={company.id} company={company} />
          ))}
        </div>

          {totalPages > 1 && (
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={onPageChange}
            />
          )}
        </>
      )}
    </div>
  );
};

const CompanyCard = ({ company }) => {
  const [showTagManager, setShowTagManager] = useState(false);
  const [availableTags, setAvailableTags] = useState([]);
  const [newTag, setNewTag] = useState('');
  const [companyTags, setCompanyTags] = useState(company.tags || []);

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  };

  const formatYear = (year) => {
    if (!year) return 'N/A';
    return Math.floor(year).toString();
  };

  const loadAvailableTags = async () => {
    try {
      const tags = await getTags();
      setAvailableTags(tags);
    } catch (error) {
      console.error('Failed to load tags:', error);
    }
  };

  const handleAddTag = async (tagName) => {
    try {
      await addTagToCompany(company.id, tagName);
      setCompanyTags([...companyTags, tagName]);
    } catch (error) {
      console.error('Failed to add tag:', error);
    }
  };

  const handleRemoveTag = async (tagName) => {
    try {
      await removeTagFromCompany(company.id, tagName);
      setCompanyTags(companyTags.filter(tag => tag !== tagName));
    } catch (error) {
      console.error('Failed to remove tag:', error);
    }
  };

  const handleCreateAndAddTag = async () => {
    if (newTag.trim() && !companyTags.includes(newTag.trim())) {
      await handleAddTag(newTag.trim());
      setNewTag('');
    }
  };

  return (
    <div className="company-card">
      <div className="company-header">
        <h3 className="company-name">{company.name}</h3>
        <a 
          href={`https://${company.domain}`} 
          target="_blank" 
          rel="noopener noreferrer"
          className="company-domain"
        >
          <Globe size={14} />
          {company.domain}
        </a>
      </div>

      <div className="company-details">
        <div className="company-detail">
          <span className="company-detail-label">Industry</span>
          <span className="company-detail-value">{company.industry}</span>
        </div>

        <div className="company-detail">
          <span className="company-detail-label">Location</span>
          <span className="company-detail-value">
            <MapPin size={12} />
            {company.locality}, {company.country}
          </span>
        </div>

        <div className="company-detail">
          <span className="company-detail-label">Founded</span>
          <span className="company-detail-value">
            <Calendar size={12} />
            {formatYear(company.year_founded)}
          </span>
        </div>

        <div className="company-detail">
          <span className="company-detail-label">Size</span>
          <span className="company-detail-value">{company.size_category || company.size_range}</span>
        </div>

        <div className="company-detail">
          <span className="company-detail-label">Employees</span>
          <span className="company-detail-value">
            <Users size={12} />
            {formatNumber(company.current_employee_estimate)}
          </span>
        </div>

        {company.linkedin_url && (
          <div className="company-detail">
            <span className="company-detail-label">LinkedIn</span>
            <a 
              href={`https://${company.linkedin_url}`}
              target="_blank"
              rel="noopener noreferrer"
              className="company-detail-value linkedin-link"
            >
              View Profile
            </a>
          </div>
        )}
      </div>

      <div className="company-tags">
        <div className="tags-header">
          <Tag size={12} className="tags-icon" />
          <span className="tags-label">Tags:</span>
          <button
            className="tag-manager-toggle"
            onClick={() => {
              setShowTagManager(!showTagManager);
              if (!showTagManager) {
                loadAvailableTags();
              }
            }}
          >
            <Plus size={12} />
            Manage
          </button>
        </div>

        {companyTags.length > 0 && (
          <div className="current-tags">
            {companyTags.map((tag, index) => (
              <span key={index} className="tag company-tag">
                {tag}
                <button
                  className="tag-remove"
                  onClick={() => handleRemoveTag(tag)}
                >
                  <X size={10} />
                </button>
              </span>
            ))}
          </div>
        )}

        {showTagManager && (
          <div className="tag-manager">
            <div className="tag-input-section">
              <input
                type="text"
                className="input tag-input"
                placeholder="Add new tag..."
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleCreateAndAddTag()}
              />
              <button
                className="btn btn-primary btn-sm"
                onClick={handleCreateAndAddTag}
                disabled={!newTag.trim()}
              >
                Add
              </button>
            </div>

            {availableTags.length > 0 && (
              <div className="available-tags-section">
                <div className="sub-label">Available Tags:</div>
                <div className="available-tags-list">
                  {availableTags
                    .filter(tag => !companyTags.includes(tag.name))
                    .map((tag) => (
                      <span
                        key={tag.id}
                        className={`tag available-tag ${tag.is_shared ? 'shared' : 'personal'}`}
                        onClick={() => handleAddTag(tag.name)}
                      >
                        {tag.name}
                      </span>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const start = Math.max(1, currentPage - 2);
      const end = Math.min(totalPages, start + maxVisible - 1);
      
      if (start > 1) {
        pages.push(1);
        if (start > 2) {
          pages.push('...');
        }
      }
      
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      if (end < totalPages) {
        if (end < totalPages - 1) {
          pages.push('...');
        }
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  return (
    <div className="pagination">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="pagination-btn"
      >
        Previous
      </button>

      {getPageNumbers().map((page, index) => (
        <button
          key={index}
          onClick={() => typeof page === 'number' && onPageChange(page)}
          disabled={page === '...'}
          className={`pagination-btn ${page === currentPage ? 'active' : ''}`}
        >
          {page}
        </button>
      ))}

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="pagination-btn"
      >
        Next
      </button>
    </div>
  );
};

export default SearchResults;

