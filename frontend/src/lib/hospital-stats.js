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
    const mixed = hospitalReviews.filter((r) => r.overall_sentiment === 'mixed').length

    const totalScore = hospitalReviews.reduce((sum, r) => sum + r.sentiment_score, 0)
    const averageScore = totalScore / hospitalReviews.length

    const derivedStarTotal = hospitalReviews.reduce((sum, r) => {
      if (r.overall_sentiment === 'positive') {
        return sum + 5
      }
      if (r.overall_sentiment === 'negative') {
        return sum + 1
      }
      return sum + 3
    }, 0)
    const averageStarRating = derivedStarTotal / hospitalReviews.length

    const aspectMap = new Map()
    hospitalReviews.forEach((review) => {
      if (review.aspects) {
        review.aspects.forEach((aspect) => {
          if (!aspectMap.has(aspect.aspect)) {
            aspectMap.set(aspect.aspect, { 
              positive: 0,
              negative: 0,
              count: 0,
            })
          }
          const aspectData = aspectMap.get(aspect.aspect)
          aspectData.count++
          if (aspect.sentiment === 'positive') {
            aspectData.positive += 1
          } else {
            aspectData.negative += 1
          }
        })
      }
    })

    const commonAspects = Array.from(aspectMap.entries())
      .map(([aspect, data]) => {
        const posCount = data.positive
        const negCount = data.negative
        const totalMentions = posCount + negCount

        // Determine sentiment: more positives -> positive, else negative
        const avgSentiment = posCount >= negCount ? 'positive' : 'negative'

        return {
          aspect,
          count: data.count,
          average_sentiment: avgSentiment,
          positive_count: posCount,
          negative_count: negCount,
          total_mentions: totalMentions,
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
        mixed,
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
