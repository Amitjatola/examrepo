const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = {
    async get(endpoint, params = {}) {
        console.log('[API DEBUG] Request:', { baseURL: BASE_URL, endpoint, fullUrl: `${BASE_URL}${endpoint}` });
        const url = new URL(`${BASE_URL}${endpoint}`);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });

        const response = await fetch(url.toString());
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        return response.json();
    },

    async post(endpoint, body = {}) {
        console.log('[API DEBUG] POST Request:', { baseURL: BASE_URL, endpoint, fullUrl: `${BASE_URL}${endpoint}`, body });
        const url = new URL(`${BASE_URL}${endpoint}`);

        const response = await fetch(url.toString(), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            // Handle error.detail which can be a string, object, or array
            let errorMessage = `API Error: ${response.statusText}`;
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (Array.isArray(error.detail)) {
                    // Pydantic validation errors format
                    errorMessage = error.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                } else if (typeof error.detail === 'object') {
                    errorMessage = error.detail.message || error.detail.msg || JSON.stringify(error.detail);
                }
            }
            throw new Error(errorMessage);
        }
        return response.json();
    },

    /**
     * Get autocomplete suggestions.
     * @param {string} query 
     * @param {number} limit 
     * @returns {Promise<string[]>}
     */
    async getSuggestions(query, limit = 5) {
        if (!query || query.length < 2) return [];
        return this.get('/search/suggestions', { q: query, limit });
    }
};
