import React, { useState, useEffect } from 'react';
import SearchFilters from './components/SearchFilters';
import SearchResults from './components/SearchResults';
import { searchCompanies, getFilterOptions } from './services/api';
import './App.css';

function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    industry: [],
    sizeRange: [],
    country: [],
    locality: [],
    yearFoundedFrom: '',
    yearFoundedTo: '',
    tags: []
  });
  const [sortBy, setSortBy] = useState('relevance');
  const [page, setPage] = useState(1);
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filterOptions, setFilterOptions] = useState({
    industries: [],
    sizeRanges: [],
    countries: [],
    localities: []
  });
  const [filterOptionsLoading, setFilterOptionsLoading] = useState(true);

  useEffect(() => {
    loadFilterOptions();
  }, []);

  useEffect(() => {
    performSearch();
  }, [searchQuery, filters, sortBy, page]);

  const loadFilterOptions = async () => {
    try {
      setFilterOptionsLoading(true);
      const options = await getFilterOptions();
      setFilterOptions(options);
    } catch (err) {
      console.error('Failed to load filter options:', err);
      // Set default empty arrays to prevent undefined errors
      setFilterOptions({
        industries: [],
        sizeRanges: [],
        countries: [],
        localities: []
      });
    } finally {
      setFilterOptionsLoading(false);
    }
  };

  const performSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const searchRequest = {
        query: searchQuery || undefined,
        industry: filters.industry.length > 0 ? filters.industry : undefined,
        size_range: filters.sizeRange.length > 0 ? filters.sizeRange : undefined,
        country: filters.country.length > 0 ? filters.country : undefined,
        locality: filters.locality.length > 0 ? filters.locality : undefined,
        year_founded_from: filters.yearFoundedFrom ? parseInt(filters.yearFoundedFrom) : undefined,
        year_founded_to: filters.yearFoundedTo ? parseInt(filters.yearFoundedTo) : undefined,
        tags: filters.tags.length > 0 ? filters.tags : undefined,
        page,
        size: 20,
        sort_by: sortBy
      };

      const response = await searchCompanies(searchRequest);
      setResults(response.companies);
      setTotal(response.total);
    } catch (err) {
      setError('Failed to search companies. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchChange = (query) => {
    setSearchQuery(query);
    setPage(1);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
    setPage(1);
  };

  const handleSortChange = (newSortBy) => {
    setSortBy(newSortBy);
    setPage(1);
  };

  const handlePageChange = (newPage) => {
    setPage(newPage);
  };

  const clearAllFilters = () => {
    setFilters({
      industry: [],
      sizeRange: [],
      country: [],
      locality: [],
      yearFoundedFrom: '',
      yearFoundedTo: '',
      tags: []
    });
    setSearchQuery('');
    setPage(1);
  };

  const totalPages = Math.ceil(total / 20);

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <h1>Company Search Dashboard</h1>
          <p>Find companies with advanced search capabilities</p>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          <div className="search-layout">
            <div className="filters-panel">
              <SearchFilters
                searchQuery={searchQuery}
                filters={filters}
                filterOptions={filterOptions}
                filterOptionsLoading={filterOptionsLoading}
                onSearchChange={handleSearchChange}
                onFilterChange={handleFilterChange}
                onClearAll={clearAllFilters}
              />
            </div>

            <div className="results-panel">
              <SearchResults
                results={results}
                total={total}
                loading={loading}
                error={error}
                sortBy={sortBy}
                page={page}
                totalPages={totalPages}
                onSortChange={handleSortChange}
                onPageChange={handlePageChange}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;

