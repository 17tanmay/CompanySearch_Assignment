import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Search companies
export const searchCompanies = async (searchRequest) => {
  try {
    const response = await api.post('/search', searchRequest);
    return response.data;
  } catch (error) {
    console.error('Search API error:', error);
    throw error;
  }
};

// Get filter options
export const getFilterOptions = async () => {
  try {
    const response = await api.get('/filters');
    return response.data;
  } catch (error) {
    console.error('Filter options API error:', error);
    throw error;
  }
};

// Get search suggestions
export const getSuggestions = async (query) => {
  try {
    const response = await api.get('/suggest', {
      params: { q: query }
    });
    return response.data.suggestions;
  } catch (error) {
    console.error('Suggestions API error:', error);
    return [];
  }
};

// Get city suggestions
export const getCitySuggestions = async (query) => {
  try {
    const response = await api.get('/suggest/cities', {
      params: { q: query }
    });
    return response.data.suggestions;
  } catch (error) {
    console.error('City suggestions API error:', error);
    return [];
  }
};

// Get company by ID
export const getCompany = async (companyId) => {
  try {
    const response = await api.get(`/companies/${companyId}`);
    return response.data;
  } catch (error) {
    console.error('Get company API error:', error);
    throw error;
  }
};

// Get all tags
export const getTags = async () => {
  try {
    const response = await api.get('/tags');
    return response.data;
  } catch (error) {
    console.error('Get tags API error:', error);
    return [];
  }
};

// Create tag
export const createTag = async (tagData) => {
  try {
    const response = await api.post('/tags', tagData);
    return response.data;
  } catch (error) {
    console.error('Create tag API error:', error);
    throw error;
  }
};

// Add tag to company
export const addTagToCompany = async (companyId, tagName) => {
  try {
    const response = await api.post(`/companies/${companyId}/tags`, null, {
      params: { tag_name: tagName }
    });
    return response.data;
  } catch (error) {
    console.error('Add tag to company API error:', error);
    throw error;
  }
};

// Remove tag from company
export const removeTagFromCompany = async (companyId, tagName) => {
  try {
    const response = await api.delete(`/companies/${companyId}/tags`, {
      params: { tag_name: tagName }
    });
    return response.data;
  } catch (error) {
    console.error('Remove tag from company API error:', error);
    throw error;
  }
};

// Get company tags
export const getCompanyTags = async (companyId) => {
  try {
    const response = await api.get(`/companies/${companyId}/tags`);
    return response.data;
  } catch (error) {
    console.error('Get company tags API error:', error);
    throw error;
  }
};

export default api;

