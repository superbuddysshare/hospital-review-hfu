/**
 * API Client Configuration and Methods
 * 
 * Backend Flask API runs on port 5000
 * Frontend Vite dev server runs on port 3001
 */

// Backend API URL (Flask service on port 5000)
const API_BASE_URL = 'http://localhost:5000'

export const api = {
  async getReviews() {
    const response = await fetch(`${API_BASE_URL}/api/reviews`)
    if (!response.ok) {
      throw new Error(`Failed to fetch reviews: ${response.statusText}`)
    }
    return response.json()
  },

  async createReview(data) {
    const response = await fetch(`${API_BASE_URL}/api/reviews`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      throw new Error(`Failed to create review: ${response.statusText}`)
    }
    return response.json()
  },

  async analyzeText(text) {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    })
    if (!response.ok) {
      throw new Error(`Failed to analyze text: ${response.statusText}`)
    }
    return response.json()
  },
}
