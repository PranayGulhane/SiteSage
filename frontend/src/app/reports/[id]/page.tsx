'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

interface Report {
  id: number
  url: string
  status: string
  seo_score: number | null
  created_at: string
  completed_at: string | null
  seo_data: any
  ai_insights: any
}

export default function ReportDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)
  const reportId = params?.id

  useEffect(() => {
    if (!reportId) return

    fetchReport()
    const interval = setInterval(fetchReport, 3000)
    return () => clearInterval(interval)
  }, [reportId])

  const fetchReport = async () => {
    try {
      const response = await fetch(`/api/reports/${reportId}`)
      const data = await response.json()
      setReport(data)
      
      if (data.status === 'completed' || data.status === 'failed') {
        setLoading(false)
      }
    } catch (error) {
      console.error('Failed to fetch report:', error)
      setLoading(false)
    }
  }

  const downloadPDF = async () => {
    window.open(`/api/reports/${reportId}/pdf`, '_blank')
  }

  const getGrade = (score: number) => {
    if (score >= 90) return { grade: 'A', color: 'text-green-600' }
    if (score >= 80) return { grade: 'B', color: 'text-blue-600' }
    if (score >= 70) return { grade: 'C', color: 'text-yellow-600' }
    if (score >= 60) return { grade: 'D', color: 'text-orange-600' }
    return { grade: 'F', color: 'text-red-600' }
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading report...</p>
        </div>
      </div>
    )
  }

  const gradeInfo = report.seo_score ? getGrade(report.seo_score) : { grade: '-', color: 'text-gray-600' }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link href="/" className="flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">SiteSage</h1>
            </Link>
            <Link
              href="/reports"
              className="text-gray-600 hover:text-primary-600 font-medium"
            >
              All Reports
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Report Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">SEO Report</h2>
              <p className="text-gray-600 break-all">{report.url}</p>
              <p className="text-sm text-gray-500 mt-2">
                Created: {new Date(report.created_at).toLocaleString()}
              </p>
            </div>
            {report.status === 'completed' && (
              <button
                onClick={downloadPDF}
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
              >
                Download PDF
              </button>
            )}
          </div>
        </div>

        {/* Status */}
        {report.status === 'processing' || report.status === 'pending' ? (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
            <div className="flex items-center">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
              <p className="text-blue-700">
                Analysis in progress... This may take a few moments.
              </p>
            </div>
          </div>
        ) : report.status === 'failed' ? (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6">
            <p className="text-red-700">Analysis failed. Please try again.</p>
          </div>
        ) : null}

        {report.status === 'completed' && report.seo_score !== null && (
          <>
            {/* Score Card */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Overall SEO Score</h3>
              <div className="flex items-center">
                <div className="text-6xl font-bold mr-6" style={{ color: gradeInfo.color.replace('text-', '') }}>
                  {report.seo_score.toFixed(1)}
                </div>
                <div>
                  <div className={`text-4xl font-bold ${gradeInfo.color}`}>
                    Grade: {gradeInfo.grade}
                  </div>
                  <div className="text-gray-600">out of 100</div>
                </div>
              </div>
            </div>

            {/* AI Insights */}
            {report.ai_insights && (
              <div className="bg-white rounded-lg shadow p-6 mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">AI-Generated Summary</h3>
                <p className="text-gray-700 whitespace-pre-wrap mb-6">
                  {report.ai_insights.summary}
                </p>

                {report.ai_insights.recommendations && report.ai_insights.recommendations.length > 0 && (
                  <>
                    <h4 className="text-lg font-semibold text-gray-900 mb-3">Recommendations</h4>
                    <ul className="space-y-2">
                      {report.ai_insights.recommendations.map((rec: string, idx: number) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-primary-600 mr-2">•</span>
                          <span className="text-gray-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}

            {/* Technical Details */}
            {report.seo_data && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Technical Details</h3>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Page Metadata</h4>
                    <dl className="space-y-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Title</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.title || 'Missing'}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Meta Description</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.meta_description || 'Missing'}</dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Structure</h4>
                    <dl className="space-y-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">H1 Tags</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.h1_tags?.length || 0}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">H2 Tags</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.h2_tags?.length || 0}</dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Images</h4>
                    <dl className="space-y-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Total Images</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.total_images || 0}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Images Without Alt</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.images_without_alt || 0}</dd>
                      </div>
                    </dl>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Links & Performance</h4>
                    <dl className="space-y-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Total Links</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.total_links || 0}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Broken Links</dt>
                        <dd className="text-sm text-gray-900">{report.seo_data.broken_links_count || 0}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Load Time</dt>
                        <dd className="text-sm text-gray-900">
                          {report.seo_data.load_time ? `${report.seo_data.load_time.toFixed(2)}s` : '-'}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
