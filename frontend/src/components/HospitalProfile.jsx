import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import {
  MapPin,
  ChatCircleDots,
  TrendUp,
  TrendDown,
  MinusCircle,
  Sparkle,
  ArrowLeft,
} from '@phosphor-icons/react'
import { motion } from 'framer-motion'

export function HospitalProfile({ hospital, onBack }) {
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [])

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-positive text-positive-foreground'
      case 'negative':
        return 'bg-negative text-negative-foreground'
      default:
        return 'bg-secondary text-foreground'
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <TrendUp size={16} weight="bold" />
      case 'negative':
        return <TrendDown size={16} weight="bold" />
      default:
        return <TrendDown size={16} weight="bold" />
    }
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const getSentimentPercentage = (count) => {
    return (count / hospital.total_reviews) * 100
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <Button variant="ghost" onClick={onBack} className="mb-2">
        <ArrowLeft size={18} className="mr-2" />
        Back to All Reviews
      </Button>

      <Card className="border-l-4 border-l-primary">
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h1
                className="text-3xl md:text-4xl font-bold mb-2"
                style={{ fontFamily: 'var(--font-newsreader)' }}
              >
                {hospital.hospital_name}
              </h1>
              {hospital.hospital_address && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <MapPin size={18} weight="fill" />
                  <span>{hospital.hospital_address}</span>
                </div>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-secondary/50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <ChatCircleDots size={20} weight="fill" className="text-primary" />
                <span className="text-sm font-semibold">Total Reviews</span>
              </div>
              <div className="text-3xl font-bold text-foreground">{hospital.total_reviews}</div>
            </div>

            <div className="bg-positive/10 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendUp size={20} weight="bold" className="text-positive" />
                <span className="text-sm font-semibold">Positive</span>
              </div>
              <div className="text-3xl font-bold text-positive">
                {hospital.sentiment_breakdown.positive}
              </div>
              <Progress
                value={getSentimentPercentage(hospital.sentiment_breakdown.positive)}
                className="mt-2 h-2"
              />
            </div>

            <div className="bg-negative/10 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendDown size={20} weight="bold" className="text-negative" />
                <span className="text-sm font-semibold">Negative</span>
              </div>
              <div className="text-3xl font-bold text-negative">
                {hospital.sentiment_breakdown.negative}
              </div>
              <Progress
                value={getSentimentPercentage(hospital.sentiment_breakdown.negative)}
                className="mt-2 h-2"
              />
            </div>
          </div>

          {hospital.common_aspects.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Sparkle size={20} weight="fill" className="text-primary" />
                <h3 className="text-lg font-semibold">Most Mentioned Aspects</h3>
              </div>
              <div className="flex flex-wrap gap-4">
                {hospital.common_aspects.map((aspect, idx) => {
                  const total = aspect.total_mentions || (aspect.positive_count + aspect.negative_count) || 1
                  const positivePct = Math.round((aspect.positive_count / total) * 100)
                  const negativePct = Math.max(0, 100 - positivePct)

                  return (
                    <div key={idx} className="min-w-[160px] flex-1">
                      <div className="flex items-center justify-between mb-1 text-xs font-semibold text-muted-foreground">
                        <span className="capitalize text-foreground">{aspect.aspect.replace(/_/g, ' ')}</span>
                        <span>{aspect.count}×</span>
                      </div>
                      <div className="relative h-10 rounded-lg overflow-hidden bg-muted border border-border">
                        <div className="absolute inset-0 flex">
                          <div
                            className="bg-positive"
                            style={{ width: `${positivePct}%` }}
                          />
                          <div
                            className="bg-negative"
                            style={{ width: `${negativePct}%` }}
                          />
                        </div>
                        <div className="relative z-10 flex items-center justify-between h-full px-2 text-sm font-bold drop-shadow">
                          <span className="text-positive bg-background/70 px-1 rounded-sm border border-positive/40">
                            {aspect.positive_count}
                          </span>
                          <span className="text-negative bg-background/70 px-1 rounded-sm border border-negative/40">
                            {aspect.negative_count}
                          </span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <div>
        <h2 className="text-2xl font-bold mb-4">All Reviews</h2>
        <Separator className="mb-4" />
        <div className="space-y-4">
          {hospital.reviews.map((review, index) => {
            const isExpanded = expanded === review.id
            const shouldTruncate = review.review_text.length > 300
            const displayText =
              isExpanded || !shouldTruncate
                ? review.review_text
                : review.review_text.slice(0, 300) + '...'

            return (
              <motion.div
                key={review.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <Card className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="text-sm text-muted-foreground mb-2">
                          {formatDate(review.timestamp)}
                        </div>
                      </div>
                      <Badge
                        className={`${getSentimentColor(review.overall_sentiment)} flex items-center gap-1.5`}
                      >
                        {getSentimentIcon(review.overall_sentiment)}
                        {review.overall_sentiment.charAt(0).toUpperCase() +
                          review.overall_sentiment.slice(1)}
                        <span className="ml-1 font-mono">{review.sentiment_score.toFixed(2)}</span>
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-foreground leading-relaxed">{displayText}</p>
                      {shouldTruncate && (
                        <button
                          onClick={() => setExpanded(isExpanded ? null : review.id)}
                          className="text-primary hover:underline text-sm font-medium mt-2"
                        >
                          {isExpanded ? 'Show Less' : 'Read More'}
                        </button>
                      )}
                    </div>

                    {review.aspects && review.aspects.length > 0 && (
                      <div>
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkle size={16} weight="fill" className="text-primary" />
                          <span className="text-sm font-semibold">Aspects</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {review.aspects.map((aspect, idx) => (
                            <Badge
                              key={idx}
                              variant="outline"
                              className={`${getSentimentColor(aspect.sentiment)} border-0 text-xs flex items-center gap-1`}
                            >
                              {aspect.aspect}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </div>
      </div>
    </motion.div>
  )
}
