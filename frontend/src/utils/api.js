const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const BY_IDS_MAX_PER_REQUEST = 100
const BY_IDS_CAP_TOTAL = 200

/** Avoid hung UI when API is down, wrong port, or server never responds */
const DEFAULT_REQUEST_TIMEOUT_MS = 20000

const fetchWithTimeout = async (urlString, fetchOptions = {}, timeoutMs = DEFAULT_REQUEST_TIMEOUT_MS) => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs)
    try {
        return await fetch(urlString, {
            ...fetchOptions,
            signal: controller.signal,
        })
    } catch (err) {
        if (err && err.name === 'AbortError') {
            const timedOut = new Error(
                `Request timed out after ${timeoutMs / 1000}s. Start the backend (e.g. port 8000) or set VITE_API_URL to your API base (must include /api/v1).`,
            )
            timedOut.name = 'TimeoutError'
            throw timedOut
        }
        throw err
    } finally {
        clearTimeout(timeoutId)
    }
}

export const api = {
    async get(endpoint, params = {}) {
        console.log('[API DEBUG] Request:', { baseURL: BASE_URL, endpoint, fullUrl: `${BASE_URL}${endpoint}` });
        const url = new URL(`${BASE_URL}${endpoint}`);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });

        const headers = {
            'Content-Type': 'application/json',
        };
        const raw = localStorage.getItem('token')
        const token = raw && String(raw).trim() ? String(raw).trim() : null
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetchWithTimeout(url.toString(), { headers });
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            let errorMessage = `API Error: ${response.statusText}`;
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMessage = error.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                } else if (typeof error.detail === 'object') {
                    errorMessage = error.detail.message || error.detail.msg || JSON.stringify(error.detail);
                }
            }
            const err = new Error(errorMessage)
            err.status = response.status
            throw err
        }
        return response.json();
    },

    async post(endpoint, body = {}) {
        console.log('[API DEBUG] POST Request:', { baseURL: BASE_URL, endpoint, fullUrl: `${BASE_URL}${endpoint}`, body });
        const url = new URL(`${BASE_URL}${endpoint}`);

        const headers = {
            'Content-Type': 'application/json',
        };
        const rawPost = localStorage.getItem('token')
        const postToken = rawPost && String(rawPost).trim() ? String(rawPost).trim() : null
        if (postToken) {
            headers['Authorization'] = `Bearer ${postToken}`;
        }

        const response = await fetchWithTimeout(url.toString(), {
            method: 'POST',
            headers,
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            let errorMessage = `API Error: ${response.statusText}`;
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMessage = error.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                } else if (typeof error.detail === 'object') {
                    errorMessage = error.detail.message || error.detail.msg || JSON.stringify(error.detail);
                }
            }
            const err = new Error(errorMessage)
            err.status = response.status
            throw err
        }
        return response.json();
    },

    async put(endpoint, body = {}) {
        console.log('[API DEBUG] PUT Request:', { baseURL: BASE_URL, endpoint, body });
        const url = new URL(`${BASE_URL}${endpoint}`);
        const headers = {
            'Content-Type': 'application/json',
        };
        const token = localStorage.getItem('token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetchWithTimeout(url.toString(), {
            method: 'PUT',
            headers,
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            let errorMessage = `API Error: ${response.statusText}`;
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMessage = error.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                } else if (typeof error.detail === 'object') {
                    errorMessage = error.detail.message || error.detail.msg || JSON.stringify(error.detail);
                }
            }
            throw new Error(errorMessage);
        }
        return response.json();
    },

    async delete(endpoint) {
        console.log('[API DEBUG] DELETE Request:', { baseURL: BASE_URL, endpoint });
        const url = new URL(`${BASE_URL}${endpoint}`);
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('token');
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const response = await fetchWithTimeout(url.toString(), { method: 'DELETE', headers });
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            let errorMessage = `API Error: ${response.statusText}`;
            if (error.detail) {
                if (typeof error.detail === 'string') {
                    errorMessage = error.detail;
                } else if (Array.isArray(error.detail)) {
                    errorMessage = error.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
                } else if (typeof error.detail === 'object') {
                    errorMessage = error.detail.message || error.detail.msg || JSON.stringify(error.detail);
                }
            }
            const err = new Error(errorMessage);
            err.status = response.status;
            throw err;
        }
        return response.json();
    },

    getSuggestions(query, limit = 5) {
        if (!query || query.length < 2) return [];
        return this.get(`/search/suggestions`, { q: query, limit });
    },

    // Discussions
    getDiscussions(questionId) {
        return this.get(`/questions/${questionId}/discussions`);
    },

    postDiscussion(questionId, content, parentId = null) {
        return this.post(`/questions/${questionId}/discussions`, { content, parent_id: parentId });
    },

    voteDiscussion(discussionId, voteType) {
        return this.post(`/discussions/${discussionId}/vote`, { vote_type: voteType });
    },

    deleteDiscussion(discussionId) {
        return this.delete(`/discussions/${discussionId}`);
    },

    addToRevision(questionId, difficulty = 'medium') {
        return this.post('/revisions/add', { question_id: questionId, difficulty });
    },

    removeFromRevision(questionId) {
        const enc = encodeURIComponent(questionId);
        return this.delete(`/revisions/${enc}`);
    },

    getRevisionQueue(params = {}) {
        return this.get('/revisions/queue/today', params);
    },

    answerRevision(questionId, quality) {
        const enc = encodeURIComponent(questionId);
        return this.post(`/revisions/${enc}/answer`, { quality });
    },

    getRevisionStats() {
        return this.get('/revisions/stats');
    },

    getRevisionState(questionId) {
        const enc = encodeURIComponent(questionId);
        return this.get(`/revisions/${enc}`);
    },

    getRevisionHistory(days = 30) {
        return this.get('/revisions/history', { days });
    },

    getMistakeMuseum(params = {}) {
        return this.get('/mistakes', params);
    },

    getMistakeSummary() {
        return this.get('/mistakes/summary');
    },

    updateMistakeAnnotation(questionId, body) {
        const enc = encodeURIComponent(questionId);
        return this.put(`/mistakes/${enc}`, body);
    },

    patchMistakeAnnotation(questionId, body) {
        const enc = encodeURIComponent(questionId);
        const url = new URL(`${BASE_URL}/mistakes/${enc}`);
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('token');
        if (token) headers['Authorization'] = `Bearer ${token}`;
        return fetchWithTimeout(url.toString(), {
            method: 'PATCH',
            headers,
            body: JSON.stringify(body),
        }).then(async (r) => {
            if (!r.ok) {
                const err = await r.json().catch(() => ({}));
                throw new Error(err.detail || r.statusText);
            }
            return r.json();
        });
    },

    addMistakeToRevision(questionId) {
        const enc = encodeURIComponent(questionId);
        return this.post(`/mistakes/${enc}/add-to-revision`);
    },

    getRepeatOffenders(params = {}) {
        return this.get('/mistakes/repeat-offenders', params);
    },

    getLeaderboard(params = {}) {
        return this.get('/leaderboard', params);
    },

    getLeaderboardInfo() {
        return this.get('/leaderboard/me');
    },

    updateLeaderboardVisibility(visibility) {
        const url = new URL(`${BASE_URL}/leaderboard/visibility`);
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('token');
        if (token) headers['Authorization'] = `Bearer ${token}`;
        return fetchWithTimeout(url.toString(), {
            method: 'PATCH',
            headers,
            body: JSON.stringify({ visibility }),
        }).then(async (r) => {
            if (!r.ok) {
                const err = await r.json().catch(() => ({}));
                const e = new Error(err.detail || r.statusText)
                e.status = r.status
                throw e
            }
            return r.json();
        });
    },

    getGapDrill(questionId) {
        return this.post('/practice/gap-drill', { question_id: questionId });
    },

    /**
     * Fetch full questions by public question_id strings; dedupes, caps at BY_IDS_CAP_TOTAL, chunks by 100.
     * @param {string[]} questionIds
     * @returns {Promise<any[]>}
     */
    async getQuestionsByIds(questionIds) {
        const unique = [...new Set((questionIds || []).filter((id) => typeof id === 'string' && id.trim()))]
        const capped = unique.slice(0, BY_IDS_CAP_TOTAL)
        const chunks = []
        for (let i = 0; i < capped.length; i += BY_IDS_MAX_PER_REQUEST) {
            chunks.push(capped.slice(i, i + BY_IDS_MAX_PER_REQUEST))
        }
        const out = []
        for (const chunk of chunks) {
            if (chunk.length === 0) continue
            const idsParam = chunk.join(',')
            const batch = await this.get('/questions/by-ids', { ids: idsParam })
            if (Array.isArray(batch)) out.push(...batch)
        }
        return out
    },
};
