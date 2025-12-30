export function aggregateHospitalStats(reviews) {
  const hospitalMap = new Map()

  reviews.forEach((review) => {
    const name = review.hospital_name
    if (!hospitalMap.has(name)) {
      hospitalMap.set(name, [])
    }
    hospitalMap.get(name).push(review)
  })

  const stats = []

  hospitalMap.forEach((hospitalReviews, hospitalName) => {
    const positive = hospitalReviews.filter((r) => r.overall_sentiment === 'positive').length
    const negative = hospitalReviews.filter((r) => r.overall_sentiment === 'negative').length
    const neutral = hospitalReviews.filter((r) => r.overall_sentiment === 'neutral').length

    const totalScore = hospitalReviews.reduce((sum, r) => sum + r.sentiment_score, 0)
    const averageScore = totalScore / hospitalReviews.length

    const totalStarRating = hospitalReviews.reduce((sum, r) => sum + (r.star_rating || 0), 0)
    const averageStarRating = totalStarRating / hospitalReviews.length

    const aspectMap = new Map()
    hospitalReviews.forEach((review) => {
      if (review.aspects) {
        review.aspects.forEach((aspect) => {
          if (!aspectMap.has(aspect.aspect)) {
            aspectMap.set(aspect.aspect, { 
              sentiments: [], 
              count: 0,
              totalStars: 0,
              starCount: 0
            })
          }
          const aspectData = aspectMap.get(aspect.aspect)
          aspectData.sentiments.push(aspect.sentiment)
          aspectData.count++
          if (aspect.star_rating) {
            aspectData.totalStars += aspect.star_rating
            aspectData.starCount++
          }
        })
      }
    })

    const commonAspects = Array.from(aspectMap.entries())
      .map(([aspect, data]) => {
        const posCount = data.sentiments.filter((s) => s === 'positive').length
        const negCount = data.sentiments.filter((s) => s === 'negative').length
        const avgSentiment =
          posCount > negCount ? 'positive' : negCount > posCount ? 'negative' : 'neutral'
        const avgStarRating = data.starCount > 0 ? data.totalStars / data.starCount : 0
        return {
          aspect,
          count: data.count,
          average_sentiment: avgSentiment,
          average_star_rating: avgStarRating
        }
      })
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)

    stats.push({
      hospital_id: hospitalReviews[0].hospital_id,
      hospital_name: hospitalName,
      hospital_address: hospitalReviews[0].hospital_address || '',
      total_reviews: hospitalReviews.length,
      average_score: averageScore,
      average_star_rating: averageStarRating,
      sentiment_breakdown: {
        positive,
        negative,
        neutral,
      },
      reviews: hospitalReviews
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .map((r) => ({
          id: r.id,
          review_text: r.review_text,
          timestamp: r.timestamp,
          overall_sentiment: r.overall_sentiment,
          sentiment_score: r.sentiment_score,
          star_rating: r.star_rating,
          aspects: r.aspects || [],
        })),
      common_aspects: commonAspects,
    })
  })

  return stats.sort((a, b) => b.total_reviews - a.total_reviews)
}
