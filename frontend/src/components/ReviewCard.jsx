import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { MapPin, TrendUp, TrendDown, MinusCircle, Sparkle, Star } from '@phosphor-icons/react'
import { motion } from 'framer-motion'
import { useState } from 'react'

export function ReviewCard({ review, index }) {
  const [expanded, setExpanded] = useState(false)
  
  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-positive text-positive-foreground'
      case 'negative':
        return 'bg-negative text-negative-foreground'
      default:
        return 'bg-neutral text-neutral-foreground'
    }
  }

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <TrendUp size={16} weight="bold" />
      case 'negative':
        return <TrendDown size={16} weight="bold" />
      default:
        return <MinusCircle size={16} weight="bold" />
    }
  }

  const getBorderColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'border-l-positive'
      case 'negative':
        return 'border-l-negative'
      default:
        return 'border-l-neutral'
    }
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        size={16}
        weight={i < rating ? 'fill' : 'regular'}
        className={i < rating ? 'text-accent' : 'text-muted-foreground'}
      />
    ))
  }

  const shouldTruncate = review.review_text.length > 300
  const displayText = expanded || !shouldTruncate 
    ? review.review_text 
    : review.review_text.slice(0, 300) + '...'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05, ease: 'easeOut' }}
    >
      <Card 
        className={`border-l-4 ${getBorderColor(review.overall_sentiment)} hover:shadow-lg transition-all duration-150 hover:scale-[1.02] cursor-default`}
      >
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h3 
                className="text-2xl font-bold mb-1"
                style={{ fontFamily: 'var(--font-newsreader)' }}
              >
                {review.hospital_name}
              </h3>
              {review.hospital_address && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <MapPin size={16} weight="fill" />
                  <span>{review.hospital_address}</span>
                </div>
              )}
              {review.star_rating && (
                <div className="flex items-center gap-2 mt-2">
                  <div className="flex gap-0.5">
                    {renderStars(review.star_rating)}
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {review.star_rating}/5
                  </span>
                </div>
              )}
            </div>
            <motion.div
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.2, type: 'spring', stiffness: 200 }}
            >
              <Badge className={`${getSentimentColor(review.overall_sentiment)} flex items-center gap-1.5 px-3 py-1.5 text-sm font-semibold`}>
                {getSentimentIcon(review.overall_sentiment)}
                {review.overall_sentiment.charAt(0).toUpperCase() + review.overall_sentiment.slice(1)}
                <span className="ml-1 font-mono">
                  {review.sentiment_score.toFixed(2)}
                </span>
              </Badge>
            </motion.div>
          </div>
          <div className="text-xs text-muted-foreground mt-2">
            {formatDate(review.timestamp)}
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div>
            <p className="text-foreground leading-relaxed">
              {displayText}
            </p>
            {shouldTruncate && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-primary hover:underline text-sm font-medium mt-2"
              >
                {expanded ? 'Show Less' : 'Read More'}
              </button>
            )}
          </div>

          {review.aspects && review.aspects.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <Sparkle size={18} weight="fill" className="text-primary" />
                <h4 className="text-sm font-semibold text-foreground">AI Analysis</h4>
              </div>
              <div className="flex flex-wrap gap-2">
                {review.aspects.map((aspect, idx) => (
                  <Badge
                    key={idx}
                    variant="outline"
                    className={`${getSentimentColor(aspect.sentiment)} border-0 flex items-center gap-1.5`}
                  >
                    {aspect.aspect}
                    {aspect.star_rating && (
                      <span className="flex items-center gap-0.5 ml-1">
                        <Star size={12} weight="fill" />
                        {aspect.star_rating}
                      </span>
                    )}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
