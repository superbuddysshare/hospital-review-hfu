import { useState, useEffect, useMemo } from 'react'
import { api } from '@/lib/api'
import { ReviewCard } from '@/components/ReviewCard'
import { ReviewDialog } from '@/components/ReviewDialog'
import { EmptyState } from '@/components/EmptyState'
import { FilterBar } from '@/components/FilterBar'
import { HospitalProfile } from '@/components/HospitalProfile'
import { aggregateHospitalStats } from '@/lib/hospital-stats'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Toaster } from '@/components/ui/sonner'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ChatCircleDots, Warning, Heartbeat, CaretLeft, CaretRight } from '@phosphor-icons/react'
import { motion } from 'framer-motion'

function App() {
  const [reviews, setReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedHospital, setSelectedHospital] = useState('all')
  const [selectedSentiment, setSelectedSentiment] = useState('all')
  const [viewingHospital, setViewingHospital] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)

  const fetchReviews = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await api.getReviews()
      setReviews(data.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      ))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reviews')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchReviews()
  }, [])

  const hospitalNames = useMemo(() => {
    const names = new Set(reviews.map((r) => r.hospital_name))
    return Array.from(names).sort()
  }, [reviews])

  const existingHospitals = useMemo(() => {
    const hospitalMap = new Map()
    reviews.forEach((r) => {
      if (!hospitalMap.has(r.hospital_name)) {
        hospitalMap.set(r.hospital_name, {
          name: r.hospital_name,
          address: r.hospital_address || '',
        })
      }
    })
    return Array.from(hospitalMap.values())
  }, [reviews])

  const filteredReviews = useMemo(() => {
    let filtered = reviews

    if (searchQuery) {
      filtered = filtered.filter((r) =>
        r.hospital_name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (selectedHospital !== 'all') {
      filtered = filtered.filter((r) => r.hospital_name === selectedHospital)
    }

    if (selectedSentiment !== 'all') {
      filtered = filtered.filter((r) => r.overall_sentiment === selectedSentiment)
    }

    return filtered
  }, [reviews, searchQuery, selectedHospital, selectedSentiment])

  const totalPages = Math.ceil(filteredReviews.length / itemsPerPage)

  const paginatedReviews = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    const endIndex = startIndex + itemsPerPage
    return filteredReviews.slice(startIndex, endIndex)
  }, [filteredReviews, currentPage, itemsPerPage])

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchQuery, selectedHospital, selectedSentiment, itemsPerPage])

  const hospitalStats = useMemo(() => {
    return aggregateHospitalStats(reviews)
  }, [reviews])

  const currentHospitalProfile = useMemo(() => {
    if (!viewingHospital) return null
    return hospitalStats.find((h) => h.hospital_name === viewingHospital)
  }, [viewingHospital, hospitalStats])

  const handleClearFilters = () => {
    setSearchQuery('')
    setSelectedHospital('all')
    setSelectedSentiment('all')
    setCurrentPage(1)
  }

  const handleHospitalClick = (hospitalName) => {
    setViewingHospital(hospitalName)
  }

  const getSentimentStats = () => {
    if (reviews.length === 0) return null
    
    const positive = reviews.filter(r => r.overall_sentiment === 'positive').length
    const negative = reviews.filter(r => r.overall_sentiment === 'negative').length
    
    return { positive, negative, total: reviews.length }
  }

  const stats = getSentimentStats()

  if (currentHospitalProfile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-secondary/20 to-background">
        <div className="max-w-5xl mx-auto px-4 py-8 md:py-12">
          <motion.header
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8 md:mb-12"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-primary text-primary-foreground p-3 rounded-xl">
                <Heartbeat size={32} weight="fill" />
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-foreground tracking-tight">
                  HealthVoice
                </h1>
                <p className="text-muted-foreground text-sm md:text-base">
                  Hospital Reviews & Sentiment Analysis
                </p>
              </div>
            </div>
          </motion.header>

          <HospitalProfile
            hospital={currentHospitalProfile}
            onBack={() => setViewingHospital(null)}
          />

          <Toaster position="top-right" />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/20 to-background">
      <div className="max-w-5xl mx-auto px-4 py-8 md:py-12">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 md:mb-12"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-xl">
              <Heartbeat size={32} weight="fill" />
            </div>
            <div>
              <h1 className="text-3xl md:text-4xl font-bold text-foreground tracking-tight">
                HealthVoice
              </h1>
              <p className="text-muted-foreground text-sm md:text-base">
                Hospital Reviews & Sentiment Analysis
              </p>
            </div>
          </div>
          
          {stats && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.3 }}
              className="bg-card rounded-lg p-4 border border-border shadow-sm"
            >
              <div className="flex items-center gap-2 mb-3">
                <ChatCircleDots size={20} weight="fill" className="text-primary" />
                <h2 className="font-semibold text-sm text-foreground">Community Insights</h2>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-2xl font-bold text-foreground">{stats.total}</div>
                  <div className="text-xs text-muted-foreground">Total Reviews</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-positive">{stats.positive}</div>
                  <div className="text-xs text-muted-foreground">Positive</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-negative">{stats.negative}</div>
                  <div className="text-xs text-muted-foreground">Negative</div>
                </div>
              </div>
            </motion.div>
          )}
        </motion.header>

        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl md:2xl font-bold text-foreground">Recent Reviews</h2>
          <div className="flex gap-2">
            <ReviewDialog onReviewCreated={fetchReviews} existingHospitals={existingHospitals} />
          </div>
        </div>

        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedHospital={selectedHospital}
          onHospitalChange={setSelectedHospital}
          selectedSentiment={selectedSentiment}
          onSentimentChange={setSelectedSentiment}
          hospitalNames={hospitalNames}
          onClearFilters={handleClearFilters}
        />

        <Separator className="mb-6" />

        {error && (
          <Alert variant="destructive" className="mb-6">
            <Warning size={18} />
            <AlertTitle>Error Loading Reviews</AlertTitle>
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchReviews}
                className="ml-4"
              >
                <ArrowClockwise size={16} className="mr-2" />
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="border border-border rounded-lg p-6 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-8 w-2/3" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                  <Skeleton className="h-8 w-24" />
                </div>
                <Skeleton className="h-20 w-full" />
                <div className="flex gap-2">
                  <Skeleton className="h-6 w-20" />
                  <Skeleton className="h-6 w-24" />
                  <Skeleton className="h-6 w-20" />
                </div>
              </div>
            ))}
          </div>
        ) : reviews.length === 0 ? (
          <EmptyState />
        ) : filteredReviews.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg mb-4">
              No reviews match your filters
            </p>
            <Button onClick={handleClearFilters} variant="outline">
              Clear Filters
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="space-y-4">
              {paginatedReviews.map((review, index) => (
                <div key={review.id} onClick={() => handleHospitalClick(review.hospital_name)}>
                  <ReviewCard review={review} index={index} />
                </div>
              ))}
            </div>

            {/* Pagination Controls */}
            {filteredReviews.length > 0 && (
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">Reviews per page:</span>
                  <Select value={itemsPerPage.toString()} onValueChange={(value) => setItemsPerPage(Number(value))}>
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="10">10</SelectItem>
                      <SelectItem value="20">20</SelectItem>
                      <SelectItem value="30">30</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, filteredReviews.length)} of {filteredReviews.length}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    <CaretLeft size={16} weight="bold" />
                    Previous
                  </Button>
                  
                  <div className="flex gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum
                      if (totalPages <= 5) {
                        pageNum = i + 1
                      } else if (currentPage <= 3) {
                        pageNum = i + 1
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i
                      } else {
                        pageNum = currentPage - 2 + i
                      }
                      
                      return (
                        <Button
                          key={pageNum}
                          variant={currentPage === pageNum ? "default" : "outline"}
                          size="sm"
                          onClick={() => setCurrentPage(pageNum)}
                          className="w-10"
                        >
                          {pageNum}
                        </Button>
                      )
                    })}
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                    <CaretRight size={16} weight="bold" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="mt-12 text-center text-sm text-muted-foreground"
        >
          <p>Powered by AI sentiment analysis • Helping you make informed healthcare decisions</p>
        </motion.footer>
      </div>

      <Toaster position="top-right" />
    </div>
  )
}

export default App
