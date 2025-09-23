import React, { useState, useEffect } from 'react';
import { Search, Filter, X } from 'lucide-react';
import { getSuggestions, getTags } from '../services/api';
import AutocompleteInput from './AutocompleteInput';

const SearchFilters = ({ 
  searchQuery, 
  filters, 
  filterOptions, 
  filterOptionsLoading,
  onSearchChange, 
  onFilterChange, 
  onClearAll 
}) => {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [tags, setTags] = useState([]);
  const [newTag, setNewTag] = useState('');

  useEffect(() => {
    loadTags();
  }, []);

  useEffect(() => {
    if (searchQuery && searchQuery.length >= 2) {
      loadSuggestions(searchQuery);
    } else {
      setSuggestions([]);
    }
  }, [searchQuery]);

  const loadTags = async () => {
    try {
      const tagsData = await getTags();
      setTags(tagsData);
    } catch (error) {
      console.error('Failed to load tags:', error);
    }
  };

  const loadSuggestions = async (query) => {
    try {
      const suggestionsData = await getSuggestions(query);
      setSuggestions(suggestionsData);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const handleSearchChange = (e) => {
    const value = e.target.value;
    onSearchChange(value);
    setShowSuggestions(value.length >= 2);
  };

  const handleSuggestionClick = (suggestion) => {
    onSearchChange(suggestion);
    setShowSuggestions(false);
  };

  const handleCheckboxChange = (filterType, value) => {
    const currentValues = filters[filterType] || [];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value];
    
    onFilterChange(filterType, newValues);
  };

  const handleYearChange = (field, value) => {
    onFilterChange(field, value);
  };

  const handleTagAdd = () => {
    if (newTag.trim() && !filters.tags.includes(newTag.trim())) {
      const newTags = [...filters.tags, newTag.trim()];
      onFilterChange('tags', newTags);
      setNewTag('');
    }
  };

  const handleTagRemove = (tagToRemove) => {
    const newTags = filters.tags.filter(tag => tag !== tagToRemove);
    onFilterChange('tags', newTags);
  };

  return (
    <div className="search-filters">
      <div className="filters-header">
        <h2>Search & Filters</h2>
        <button 
          className="btn btn-outline btn-sm"
          onClick={onClearAll}
        >
          <X size={16} />
          Clear All
        </button>
      </div>

      {/* Free Text Search */}
      <div className="filter-section">
        <label className="label">Free Text Search</label>
        <div className="search-input-container">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="input"
            placeholder="Search companies..."
            value={searchQuery}
            onChange={handleSearchChange}
            onFocus={() => setShowSuggestions(searchQuery.length >= 2)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          />
          {showSuggestions && suggestions.length > 0 && (
            <div className="suggestions-dropdown">
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className="suggestion-item"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Industry Filter */}
      <div className="filter-section">
        <label className="label">Industry</label>
        <div className="checkbox-group">
          {filterOptionsLoading ? (
            <div className="loading">Loading industries...</div>
          ) : (
            (filterOptions.industries || []).map((industry) => (
              <label key={industry} className="checkbox-label">
                <input
                  type="checkbox"
                  className="checkbox"
                  checked={filters.industry?.includes(industry) || false}
                  onChange={() => handleCheckboxChange('industry', industry)}
                />
                {industry}
              </label>
            ))
          )}
        </div>
      </div>

      {/* Company Size Filter */}
      <div className="filter-section">
        <label className="label">Company Size</label>
        <div className="checkbox-group">
          {filterOptionsLoading ? (
            <div className="loading">Loading size ranges...</div>
          ) : (
            [
              "Large (10001+)",
              "Medium (1000-10000)", 
              "Small (<1000)"
            ].map((sizeRange) => (
              <label key={sizeRange} className="checkbox-label">
                <input
                  type="checkbox"
                  className="checkbox"
                  checked={filters.sizeRange?.includes(sizeRange) || false}
                  onChange={() => handleCheckboxChange('sizeRange', sizeRange)}
                />
                {sizeRange}
              </label>
            ))
          )}
        </div>
      </div>

      {/* Location Filter */}
      <div className="filter-section">
        <label className="label">Location</label>
        <div className="location-filters">
          <div className="location-field">
            <label className="sub-label">Country</label>
            <select
              className="input"
              value={filters.country[0] || ''}
              onChange={(e) => onFilterChange('country', e.target.value ? [e.target.value] : [])}
              disabled={filterOptionsLoading}
            >
              <option value="">{filterOptionsLoading ? 'Loading...' : 'Select Country'}</option>
              {(filterOptions.countries || []).map((country) => (
                <option key={country} value={country}>
                  {country}
                </option>
              ))}
            </select>
          </div>
          <div className="location-field">
            <label className="sub-label">City</label>
            <AutocompleteInput
              value={filters.locality[0] || ''}
              onChange={(value) => onFilterChange('locality', value ? [value] : [])}
              placeholder="Type city name..."
              disabled={filterOptionsLoading}
              maxSuggestions={5}
            />
          </div>
        </div>
      </div>

      {/* Founding Year Filter */}
      <div className="filter-section">
        <label className="label">Founding Year</label>
        <div className="year-filters">
          <div className="year-field">
            <label className="sub-label">From</label>
            <input
              type="number"
              className="input"
              placeholder="1900"
              value={filters.yearFoundedFrom}
              onChange={(e) => handleYearChange('yearFoundedFrom', e.target.value)}
            />
          </div>
          <div className="year-field">
            <label className="sub-label">To</label>
            <input
              type="number"
              className="input"
              placeholder="2000"
              value={filters.yearFoundedTo}
              onChange={(e) => handleYearChange('yearFoundedTo', e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Tags Filter */}
      <div className="filter-section">
        <label className="label">Tags</label>
        <div className="tags-container">
          <div className="tag-input">
            <input
              type="text"
              className="input"
              placeholder="Add tag..."
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleTagAdd()}
            />
            <button 
              className="btn btn-primary btn-sm"
              onClick={handleTagAdd}
              disabled={!newTag.trim()}
            >
              Add
            </button>
          </div>
          
          {filters.tags.length > 0 && (
            <div className="selected-tags">
              {filters.tags.map((tag) => (
                <span key={tag} className="tag selected-tag">
                  {tag}
                  <button
                    className="tag-remove"
                    onClick={() => handleTagRemove(tag)}
                  >
                    <X size={12} />
                  </button>
                </span>
              ))}
            </div>
          )}

          {(tags || []).length > 0 && (
            <div className="available-tags">
              <div className="sub-label">Available Tags:</div>
              <div className="tag-list">
                {(tags || []).map((tag) => (
                  <span
                    key={tag.id}
                    className={`tag ${tag.is_shared ? 'shared' : 'personal'}`}
                    onClick={() => {
                      if (!filters.tags.includes(tag.name)) {
                        onFilterChange('tags', [...filters.tags, tag.name]);
                      }
                    }}
                  >
                    {tag.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchFilters;

