'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await fetch('/api/reports', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      })

      if (!response.ok) {
        throw new Error('Failed to submit URL')
      }

      const data = await response.json()
      router.push(`/reports/${data.id}`)
    } catch (err) {
      setError('Failed to submit URL. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">SiteSage</h1>
            </div>
            <Link
              href="/reports"
              className="text-gray-600 hover:text-primary-600 font-medium"
            >
              View All Reports
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold text-gray-900 mb-4">
            Automated SEO Performance Analyzer
          </h2>
          <p className="text-xl text-gray-600">
            Get instant AI-powered insights to improve your website's SEO
          </p>
        </div>

        {/* URL Submission Form */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <form onSubmit={handleSubmit}>
            <div className="mb-6">
              <label
                htmlFor="url"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Enter Website URL
              </label>
              <input
                type="url"
                id="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900"
              />
            </div>

            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium text-lg transition-colors"
            >
              {loading ? 'Analyzing...' : 'Analyze Website'}
            </button>
          </form>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-16">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-primary-600 text-3xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold mb-2">Deep Analysis</h3>
            <p className="text-gray-600">
              Comprehensive crawling of your website to extract SEO data
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-primary-600 text-3xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold mb-2">AI Insights</h3>
            <p className="text-gray-600">
              LLM-powered recommendations for optimization
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-primary-600 text-3xl mb-4">📊</div>
            <h3 className="text-lg font-semibold mb-2">Detailed Reports</h3>
            <p className="text-gray-600">
              Actionable reports with scores and recommendations
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
