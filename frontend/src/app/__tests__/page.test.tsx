import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Home from '../page'

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders the main heading', () => {
    render(<Home />)
    expect(screen.getByText(/Automated SEO Performance Analyzer/i)).toBeInTheDocument()
  })

  it('renders the URL input field', () => {
    render(<Home />)
    const input = screen.getByPlaceholderText(/https:\/\/example.com/i)
    expect(input).toBeInTheDocument()
  })

  it('renders the analyze button', () => {
    render(<Home />)
    const button = screen.getByRole('button', { name: /Analyze Website/i })
    expect(button).toBeInTheDocument()
  })

  it('shows loading state when submitting', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ id: 1, url: 'https://example.com', status: 'pending' }),
    })

    render(<Home />)
    
    const input = screen.getByPlaceholderText(/https:\/\/example.com/i)
    const button = screen.getByRole('button', { name: /Analyze Website/i })

    fireEvent.change(input, { target: { value: 'https://example.com' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/Analyzing.../i)).toBeInTheDocument()
    })
  })

  it('displays error message on failed submission', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
    })

    render(<Home />)
    
    const input = screen.getByPlaceholderText(/https:\/\/example.com/i)
    const button = screen.getByRole('button', { name: /Analyze Website/i })

    fireEvent.change(input, { target: { value: 'https://example.com' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText(/Failed to submit URL/i)).toBeInTheDocument()
    })
  })

  it('displays feature cards', () => {
    render(<Home />)
    expect(screen.getByText(/Deep Analysis/i)).toBeInTheDocument()
    expect(screen.getByText(/AI Insights/i)).toBeInTheDocument()
    expect(screen.getByText(/Detailed Reports/i)).toBeInTheDocument()
  })
})
